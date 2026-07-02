/**
 * UpgradePrompt — shown when a user on Free tier tries to access a paid feature.
 *
 * Usage:
 *   <UpgradePrompt message="Full portfolio analytics is available on the Single plan ($10/month)." />
 */
import { NavLink } from 'react-router-dom'

type UpgradePromptProps = {
  message?: string
}

const DEFAULT_MESSAGE =
  'This feature is available on the Single plan ($10/month). Upgrade to unlock the full experience.'

export function UpgradePrompt({ message = DEFAULT_MESSAGE }: UpgradePromptProps) {
  return (
    <div className="upgrade-prompt">
      <p className="upgrade-prompt__message">{message}</p>
      <NavLink to="/billing" className="upgrade-prompt__link">
        View plans &amp; upgrade →
      </NavLink>
    </div>
  )
}
