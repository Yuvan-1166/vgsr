/**
 * Schema parser that handles SQL DDL, JSON, and CSV formats
 */

export function parseSchema(text) {
  const trimmed = text.trim()
  if (!trimmed) throw new Error('Empty schema input')

  // Try JSON first
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    return parseJSONSchema(trimmed)
  }

  // Try SQL DDL
  if (trimmed.toUpperCase().includes('CREATE TABLE')) {
    return parseSQLDDL(trimmed)
  }

  // Try CSV-like
  if (trimmed.includes(',')) {
    return parseCSVSchema(trimmed)
  }

  throw new Error('Could not detect schema format. Use SQL CREATE TABLE, JSON, or CSV.')
}

function parseSQLDDL(text) {
  const tables = []
  const tableRegex = /CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"']?(\w+)[`"']?\s*\(([\s\S]*?)\)\s*;/gi
  let match

  while ((match = tableRegex.exec(text)) !== null) {
    const tableName = match[1]
    const columnsDef = match[2]
    const columns = parseColumnDefs(columnsDef)
    tables.push({ name: tableName, columns })
  }

  if (tables.length === 0) {
    throw new Error('No CREATE TABLE statements found')
  }

  return { tables }
}

function parseColumnDefs(columnsDef) {
  const columns = []
  // Split by commas, but not commas inside parentheses
  const parts = splitByComma(columnsDef)

  for (const part of parts) {
    const trimmed = part.trim()
    if (!trimmed) continue

    // Skip constraints
    const upper = trimmed.toUpperCase()
    if (upper.startsWith('PRIMARY KEY') || upper.startsWith('FOREIGN KEY') ||
        upper.startsWith('UNIQUE') || upper.startsWith('INDEX') ||
        upper.startsWith('CHECK') || upper.startsWith('CONSTRAINT') ||
        upper.startsWith('KEY')) {
      continue
    }

    // Parse column definition
    const colMatch = trimmed.match(/^[`"']?(\w+)[`"']?\s+([\w()., ]+)/i)
    if (!colMatch) continue

    const colName = colMatch[1]
    let colType = colMatch[2].trim()

    const pk = upper.includes('PRIMARY KEY')
    const nullable = !upper.includes('NOT NULL')

    // Check for REFERENCES
    let fk = null
    const fkMatch = trimmed.match(/REFERENCES\s+[`"']?(\w+)[`"']?\s*\([`"']?(\w+)[`"']?\)/i)
    if (fkMatch) {
      fk = `${fkMatch[1]}(${fkMatch[2]})`
    }

    // Clean up type - remove trailing constraints
    colType = colType
      .replace(/\s+PRIMARY\s+KEY/i, '')
      .replace(/\s+NOT\s+NULL/i, '')
      .replace(/\s+NULL/i, '')
      .replace(/\s+DEFAULT\s+.*/i, '')
      .replace(/\s+AUTO_INCREMENT/i, '')
      .replace(/\s+UNSIGNED/i, '')
      .replace(/\s+REFERENCES\s+.*/i, '')
      .trim()

    columns.push({ name: colName, type: colType, pk, nullable, fk })
  }

  return columns
}

function splitByComma(str) {
  const parts = []
  let depth = 0
  let current = ''

  for (const ch of str) {
    if (ch === '(') depth++
    else if (ch === ')') depth--
    else if (ch === ',' && depth === 0) {
      parts.push(current)
      current = ''
      continue
    }
    current += ch
  }
  if (current.trim()) parts.push(current)
  return parts
}

function parseJSONSchema(text) {
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('Invalid JSON format')
  }

  // Handle array of tables
  if (Array.isArray(data)) {
    return { tables: data.map(normalizeJSONTable) }
  }

  // Handle { tables: [...] } format
  if (data.tables && Array.isArray(data.tables)) {
    return { tables: data.tables.map(normalizeJSONTable) }
  }

  // Handle { tableName: { columns: [...] } } format
  const tableNames = Object.keys(data)
  if (tableNames.length > 0 && typeof data[tableNames[0]] === 'object') {
    const tables = tableNames.map(name => {
      const def = data[name]
      if (Array.isArray(def)) {
        return { name, columns: def.map(normalizeJSONColumn) }
      }
      if (def.columns && Array.isArray(def.columns)) {
        return { name, columns: def.columns.map(normalizeJSONColumn) }
      }
      // Object with column names as keys
      return {
        name,
        columns: Object.entries(def).map(([colName, colType]) => ({
          name: colName,
          type: typeof colType === 'string' ? colType : 'VARCHAR(255)',
          pk: false,
          nullable: true,
          fk: null,
        })),
      }
    })
    return { tables }
  }

  throw new Error('Unrecognized JSON schema format')
}

function normalizeJSONTable(table) {
  const name = table.name || table.table_name || table.tableName || 'unknown'
  const cols = table.columns || table.fields || table.cols || []
  return {
    name,
    columns: Array.isArray(cols) ? cols.map(normalizeJSONColumn) : [],
  }
}

function normalizeJSONColumn(col) {
  if (typeof col === 'string') {
    return { name: col, type: 'VARCHAR(255)', pk: false, nullable: true, fk: null }
  }
  return {
    name: col.name || col.column_name || col.columnName || 'unknown',
    type: col.type || col.data_type || col.dataType || 'VARCHAR(255)',
    pk: col.pk || col.primary_key || col.primaryKey || false,
    nullable: col.nullable ?? true,
    fk: col.fk || col.foreign_key || col.foreignKey || null,
  }
}

function parseCSVSchema(text) {
  const lines = text.split('\n').filter(l => l.trim())
  if (lines.length === 0) throw new Error('Empty CSV input')

  const tables = []
  let currentTable = null

  for (const line of lines) {
    const parts = line.split(',').map(p => p.trim().replace(/^["']|["']$/g, ''))
    if (parts.length < 2) continue

    // If first part looks like a table name marker
    if (parts[0].toUpperCase() === 'TABLE' || parts[0].toUpperCase().startsWith('TABLE:')) {
      const tableName = parts[0].toUpperCase().startsWith('TABLE:')
        ? parts.slice(1).join('_').replace(/[^a-zA-Z0-9_]/g, '')
        : parts[1]?.replace(/[^a-zA-Z0-9_]/g, '')
      if (tableName) {
        currentTable = { name: tableName, columns: [] }
        tables.push(currentTable)
      }
      continue
    }

    // If first line has no table header, create default
    if (!currentTable) {
      currentTable = { name: 'data', columns: [] }
      tables.push(currentTable)
    }

    // CSV: column_name, type, pk, nullable
    if (parts.length >= 2) {
      currentTable.columns.push({
        name: parts[0],
        type: parts[1] || 'VARCHAR(255)',
        pk: parts[2]?.toLowerCase() === 'true' || parts[2]?.toLowerCase() === 'pk',
        nullable: parts[3]?.toLowerCase() !== 'false',
        fk: parts[4] || null,
      })
    }
  }

  if (tables.length === 0) throw new Error('Could not parse CSV schema')
  return { tables }
}
