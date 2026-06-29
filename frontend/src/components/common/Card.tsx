import type { PropsWithChildren } from 'react'

type CardProps = PropsWithChildren<{
  title?: string
  subtitle?: string
}>

export function Card({ children, title, subtitle }: CardProps) {
  return (
    <section className="card">
      {(title || subtitle) && (
        <header className="card__header">
          {title && <h2>{title}</h2>}
          {subtitle && <p>{subtitle}</p>}
        </header>
      )}
      {children}
    </section>
  )
}
