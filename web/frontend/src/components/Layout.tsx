import { Link, useLocation } from 'react-router-dom'
import { FileSpreadsheet, Table, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const navItems = [
    { href: '/', label: 'Data Cleaning', icon: Sparkles },
    { href: '/files', label: 'Data Files', icon: Table },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-8 flex items-center gap-2">
            <FileSpreadsheet className="h-6 w-6 text-primary" />
            <span className="font-bold text-lg">Data Cleaner</span>
          </div>
          <nav className="flex items-center gap-6">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={cn(
                    'flex items-center gap-2 text-sm font-medium transition-colors hover:text-primary',
                    isActive ? 'text-primary' : 'text-muted-foreground'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">{children}</main>

      {/* Footer */}
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-14 md:flex-row">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            Data Cleaning Application • Built with Flask + React + shadcn/UI
          </p>
        </div>
      </footer>
    </div>
  )
}
