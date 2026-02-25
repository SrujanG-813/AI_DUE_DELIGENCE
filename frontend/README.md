# AI Due Diligence Engine - React Frontend

Modern, beautiful web interface built with React, TypeScript, and Tailwind CSS.

## Features

- 🎨 **Beautiful UI** - Modern gradient design with glass-morphism effects
- 📁 **Drag & Drop** - Easy file upload with visual feedback
- 📊 **Interactive Charts** - Visualize risk data with Recharts
- 🎯 **Real-time Progress** - Live analysis progress tracking
- 📱 **Responsive** - Works on desktop, tablet, and mobile
- ⚡ **Fast** - Built with Vite for lightning-fast development
- 🎭 **Animations** - Smooth transitions and micro-interactions

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Vite** - Next-generation build tool
- **Recharts** - Composable charting library
- **React Dropzone** - File upload component
- **React Markdown** - Markdown rendering
- **Lucide React** - Beautiful icon library

## Prerequisites

- Node.js 18+ ([Download](https://nodejs.org/))
- npm or yarn package manager

## Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   Navigate to `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Header.tsx       # App header
│   │   ├── FileUpload.tsx   # File upload component
│   │   ├── AnalysisProgress.tsx  # Progress indicator
│   │   ├── ResultsDashboard.tsx  # Results overview
│   │   ├── FindingsCard.tsx      # Risk findings display
│   │   ├── RiskChart.tsx         # Data visualization
│   │   ├── InconsistenciesCard.tsx  # Inconsistencies display
│   │   └── RiskMemoViewer.tsx    # Markdown memo viewer
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # App entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── tailwind.config.js       # Tailwind config
├── vite.config.ts           # Vite config
└── README.md                # This file
```

## Configuration

### API Endpoint

The frontend connects to the FastAPI backend at `http://localhost:8000`. This is configured in `vite.config.ts`:

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### Tailwind CSS

Custom theme configuration in `tailwind.config.js`:
- Custom color palette (primary, danger, warning, success)
- Custom animations (fade-in, slide-up, pulse-slow)
- Glass-morphism effects
- Gradient utilities

## Development

### Adding New Components

1. Create component file in `src/components/`
2. Use TypeScript for type safety
3. Follow existing naming conventions
4. Use Tailwind CSS for styling

Example:
```typescript
interface MyComponentProps {
  title: string
  data: any[]
}

export default function MyComponent({ title, data }: MyComponentProps) {
  return (
    <div className="glass-effect rounded-2xl p-6">
      <h3 className="text-xl font-bold">{title}</h3>
      {/* Component content */}
    </div>
  )
}
```

### Styling Guidelines

- Use Tailwind utility classes
- Leverage custom classes: `glass-effect`, `card-hover`, `gradient-text`, `btn-primary`
- Follow color scheme: blue/indigo for primary, red for danger, yellow for warning, green for success
- Use consistent spacing: 4, 6, 8, 12 for padding/margins

### Type Safety

All API responses and component props are typed. See `src/types/index.ts` for type definitions.

## Building for Production

1. **Build the app:**
   ```bash
   npm run build
   ```

2. **Preview production build:**
   ```bash
   npm run preview
   ```

3. **Deploy:**
   The `dist/` folder contains the production build. Deploy to:
   - Vercel
   - Netlify
   - AWS S3 + CloudFront
   - Any static hosting service

## Troubleshooting

### Port Already in Use

If port 3000 is in use, change it in `vite.config.ts`:
```typescript
server: {
  port: 3001, // Change to any available port
}
```

### API Connection Issues

Ensure the FastAPI backend is running on port 8000:
```bash
python api_server.py
```

### Build Errors

Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Lazy loading for components
- Optimized bundle size with Vite
- Tree-shaking for unused code
- CSS purging in production

## Accessibility

- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- Screen reader friendly

## License

Same as parent project - Educational use only.

---

**Need Help?** Check the main README.md or open an issue.
