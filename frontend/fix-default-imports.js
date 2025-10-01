const fs = require('fs');
const { execSync } = require('child_process');

const files = execSync('grep -rl "^import [A-Z].*from .@/components/ui" src --include="*.tsx" --include="*.ts"', 
  { encoding: 'utf8' }).split('\n').filter(f => f.trim());

let fixedCount = 0;

files.forEach(file => {
  if (!file) return;
  
  try {
    let content = fs.readFileSync(file, 'utf8');
    const original = content;
    
    // Fix default imports to named imports
    // Match: import ComponentName from '@/components/ui';
    // Replace with: import { ComponentName } from '@/components/ui';
    content = content.replace(
      /^import\s+([A-Z]\w+)\s+from\s+'@\/components\/ui';?$/gm,
      "import { $1 } from '@/components/ui';"
    );
    
    if (content !== original) {
      fs.writeFileSync(file, content, 'utf8');
      console.log(`Fixed: ${file}`);
      fixedCount++;
    }
  } catch (err) {
    console.error(`Error: ${file}:`, err.message);
  }
});

console.log(`\n✅ Fixed ${fixedCount} files with default imports`);
