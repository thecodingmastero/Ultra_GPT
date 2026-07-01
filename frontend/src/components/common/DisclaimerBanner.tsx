import type { ReactNode } from 'react'

type DisclaimerBannerProps = {
  children?: ReactNode
}

export function DisclaimerBanner({ children }: DisclaimerBannerProps) {
  return (
    <div className="disclaimer-banner" role="note">
      {children ?? (
        <>
          <strong>Educational use only.</strong> The Better Investor helps you learn about investing principles and portfolio risks, but it does not provide personalized financial advice.
        </>
      )}
    </div>
  )
}
