import Link from 'next/link'
import type { BrandProps } from '@/types/components'

export default function Brand({ className = '', showText = true }: BrandProps) {
  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {showText && (
        <Link 
          href="/" 
          className="text-xl font-bold text-gray-900 dark:text-white hover:text-brand-primary transition-colors"
          aria-label="MiraiWorks Home"
        >
          MiraiWorks
        </Link>
      )}
    </div>
  )
}