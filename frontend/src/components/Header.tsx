import { FileText } from 'lucide-react'

export default function Header() {
  return (
    <header className="glass-effect border-b border-white/20 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">
                AI Due Diligence Engine
              </h1>
              <p className="text-xs text-gray-500">Intelligent Risk Analysis Platform</p>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center space-x-6">
            <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">
              Dashboard
            </a>
            <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">
              Documentation
            </a>
            <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">
              API
            </a>
            <button className="btn-primary text-sm py-2 px-4">
              Get Started
            </button>
          </nav>
        </div>
      </div>
    </header>
  )
}
