const fs = require('fs');
const path = require('path');

// Recursively find all TypeScript files
function findTypeScriptFiles(dir, excludeDirs = []) {
  let results = [];
  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      const dirName = path.basename(fullPath);
      if (!excludeDirs.includes(dirName)) {
        results = results.concat(findTypeScriptFiles(fullPath, excludeDirs));
      }
    } else if (item.endsWith('.ts') || item.endsWith('.tsx')) {
      results.push(fullPath);
    }
  }

  return results;
}

// Extract type definitions from file content
function extractTypes(content, filePath) {
  const types = [];
  const lines = content.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Match interface and type declarations
    const interfaceMatch = trimmed.match(/^(export\s+)?interface\s+(\w+)/);
    const typeMatch = trimmed.match(/^(export\s+)?type\s+(\w+)/);

    if (interfaceMatch) {
      types.push({
        type: 'interface',
        name: interfaceMatch[2],
        exported: !!interfaceMatch[1],
        line: i + 1,
        filePath: filePath
      });
    } else if (typeMatch) {
      types.push({
        type: 'type',
        name: typeMatch[2],
        exported: !!typeMatch[1],
        line: i + 1,
        filePath: filePath
      });
    }
  }

  return types;
}

// Main execution
const frontendSrc = path.join(__dirname, '..', 'frontend', 'src');
const excludeDirs = ['types', 'node_modules', '.next', 'dist', 'build'];

console.log('Scanning for TypeScript files...\n');

const allFiles = findTypeScriptFiles(frontendSrc, excludeDirs);
console.log(`Found ${allFiles.length} TypeScript files to analyze\n`);

const typesByFile = {};
const typesByDomain = {
  api: [],
  hooks: [],
  components: [],
  app: [],
  other: []
};

let totalTypes = 0;

// Process each file
for (const filePath of allFiles) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const types = extractTypes(content, filePath);

  if (types.length > 0) {
    const relativePath = path.relative(frontendSrc, filePath);
    typesByFile[relativePath] = types;
    totalTypes += types.length;

    // Categorize by domain
    if (relativePath.startsWith('api')) {
      typesByDomain.api.push(...types);
    } else if (relativePath.startsWith('hooks')) {
      typesByDomain.hooks.push(...types);
    } else if (relativePath.startsWith('components')) {
      typesByDomain.components.push(...types);
    } else if (relativePath.startsWith('app')) {
      typesByDomain.app.push(...types);
    } else {
      typesByDomain.other.push(...types);
    }
  }
}

// Generate report
const report = {
  summary: {
    totalFiles: Object.keys(typesByFile).length,
    totalTypes: totalTypes,
    exportedTypes: Object.values(typesByFile).flat().filter(t => t.exported).length,
    nonExportedTypes: Object.values(typesByFile).flat().filter(t => !t.exported).length
  },
  byDomain: {
    api: typesByDomain.api.length,
    hooks: typesByDomain.hooks.length,
    components: typesByDomain.components.length,
    app: typesByDomain.app.length,
    other: typesByDomain.other.length
  },
  files: typesByFile
};

// Write detailed report
const outputPath = path.join(__dirname, 'types-analysis-report.json');
fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));

console.log('===== TYPE ANALYSIS SUMMARY =====\n');
console.log(`Total files with inline types: ${report.summary.totalFiles}`);
console.log(`Total type definitions found: ${report.summary.totalTypes}`);
console.log(`  - Exported: ${report.summary.exportedTypes}`);
console.log(`  - Non-exported: ${report.summary.nonExportedTypes}\n`);

console.log('===== TYPES BY DOMAIN =====');
console.log(`API files:        ${report.byDomain.api} types`);
console.log(`Hooks:            ${report.byDomain.hooks} types`);
console.log(`Components:       ${report.byDomain.components} types`);
console.log(`App (pages):      ${report.byDomain.app} types`);
console.log(`Other:            ${report.byDomain.other} types\n`);

console.log(`\nDetailed report saved to: ${outputPath}\n`);

// Print top 20 files with most types
const filesSorted = Object.entries(typesByFile)
  .map(([file, types]) => ({ file, count: types.length }))
  .sort((a, b) => b.count - a.count)
  .slice(0, 20);

console.log('===== TOP 20 FILES WITH MOST TYPES =====');
filesSorted.forEach(({ file, count }) => {
  console.log(`${count.toString().padStart(3)} types - ${file}`);
});
