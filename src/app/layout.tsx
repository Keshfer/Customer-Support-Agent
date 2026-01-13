import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Customer Support AI Agent',
  description: 'AI-powered customer support chat agent',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-white antialiased">
        {children}
      </body>
    </html>
  )
}
