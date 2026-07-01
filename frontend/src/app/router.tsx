import { createBrowserRouter } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { AccountPage } from '../pages/AccountPage'
import { AssistantPage } from '../pages/AssistantPage'
import { LandingPage } from '../pages/LandingPage'
import { LearnPage } from '../pages/LearnPage'
import { LoginPage } from '../pages/LoginPage'
import { MarketPage } from '../pages/MarketPage'
import { PortfolioPage } from '../pages/PortfolioPage'
import { PricingPage } from '../pages/PricingPage'
import { RegisterPage } from '../pages/RegisterPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: 'assistant', element: <AssistantPage /> },
      { path: 'portfolio', element: <PortfolioPage /> },
      { path: 'market', element: <MarketPage /> },
      { path: 'learn', element: <LearnPage /> },
      { path: 'pricing', element: <PricingPage /> },
      { path: 'account', element: <AccountPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
    ],
  },
])
