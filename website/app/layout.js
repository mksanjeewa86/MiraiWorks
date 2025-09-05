import './globals.css'

export const metadata = {
  title: 'MiraiWorks - Future-Forward Solutions',
  description: 'Innovative technology solutions for tomorrow',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}