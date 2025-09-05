import { Link } from 'react-router-dom'

interface BrandProps {
  className?: string
  showText?: boolean
}

export default function Brand({ className = '', showText = true }: BrandProps) {
  return (
    <Link 
      to="/" 
      className={`flex items-center space-x-3 ${className}`}
      aria-label="MiraiWorks Home"
    >
      <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-lg">
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