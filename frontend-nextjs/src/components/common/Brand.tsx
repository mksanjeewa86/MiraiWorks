import Link from 'next/link'

interface BrandProps {
  className?: string
  showText?: boolean
}

export default function Brand({ className = '', showText = true }: BrandProps) {
  return (
    <Link 
      href="/" 
      className={`flex items-center space-x-3 ${className}`}
      aria-label="MiraiWorks Home"
    >
      <div className="w-8 h-8 bg-gradient-to-br from-brand-primary to-brand-primary-dark rounded-xl flex items-center justify-center shadow-lg">
        <span className="text-white font-bold text-sm">MW</span>
      </div>
      {showText && (
        <span className="text-xl font-bold text-gray-900 dark:text-white">
          MiraiWorks
        </span>
      )}
    </Link>
  )
}