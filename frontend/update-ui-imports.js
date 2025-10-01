const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Find all files with ui component imports
const files = execSync('find src -name "*.tsx" -o -name "*.ts"', { encoding: 'utf8' })
  .split('\n')
  .filter(f => f.trim());

let updatedCount = 0;

files.forEach(file => {
  if (!file) return;
  
  try {
    const content = fs.readFileSync(file, 'utf8');
    
    // Check if file has any @/components/ui/ imports (not already using barrel)
    if (content.includes("from '@/components/ui/") || content.includes('from "@/components/ui/')) {
      console.log(`Updating: ${file}`);
      
      // Replace all individual imports with barrel import path
      const updated = content.replace(
        /from ['"]@\/components\/ui\/[^'"]+['"]/g,
        "from '@/components/ui'"
      );
      
      if (updated !== content) {
        fs.writeFileSync(file, updated, 'utf8');
        updatedCount++;
      }
    }
  } catch (err) {
    console.error(`Error processing ${file}:`, err.message);
  }
});

console.log(`\n✅ Updated ${updatedCount} files to use barrel export`);
