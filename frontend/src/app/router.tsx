import { createBrowserRouter } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { AssistantPage } from '../pages/AssistantPage'
import { DashboardPage } from '../pages/DashboardPage'
import { LandingPage } from '../pages/LandingPage'
import { LearnPage } from '../pages/LearnPage'
import { LoginPage } from '../pages/LoginPage'
import { MarketPage } from '../pages/MarketPage'
import { PortfolioPage } from '../pages/PortfolioPage'
import { PricingPage } from '../pages/PricingPage'
import { ProfilePage } from '../pages/ProfilePage'
import { RegisterPage } from '../pages/RegisterPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'ask-ai', element: <AssistantPage /> },
      { path: 'assistant', element: <AssistantPage /> },
      { path: 'portfolio-lab', element: <PortfolioPage /> },
      { path: 'portfolio', element: <PortfolioPage /> },
      { path: 'market', element: <MarketPage /> },
      { path: 'learn', element: <LearnPage /> },
      { path: 'profile', element: <ProfilePage /> },
      { path: 'account', element: <ProfilePage /> },
      { path: 'pricing', element: <PricingPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
    ],
  },
])
