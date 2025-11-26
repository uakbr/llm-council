# UI/UX Review – LLM Council (2025-11-26)

Comprehensive visual and interaction audit based on the current frontend (Settings, chat, stages, sidebar). No code changes made—this is a list of issues to address.

## Settings page (highest impact)
- **Action buttons visually inside the preset panel**: The dashed “Everything else is preconfigured” box wraps around the `Save API Key` / `Test Connection` buttons in the current layout, so the primary actions look scoped to the preset info instead of the whole form. Likely caused by missing separation/margin after the preset panel.
- **Broken content when settings fail to load**: When `/api/settings` errors, the error banner shows but the preset cards render empty, leaving lone bullets/empty pills (endpoint dot, blank council/chair chips). There’s no fallback defaults, retry affordance, or hiding of the preset panel on failure.
- **Persistent error state**: Once an error is set it remains until a successful save/test; changing the key or retrying load doesn’t clear it, which keeps the big red banner even if the user fixes connectivity.
- **Group hierarchy unclear**: The preset box uses the same card as the form fields, so hierarchy between “user input” (API key) and “reference info” (endpoint/models) is blurred. The buttons also sit at the same level as the preset box, so eye flow is muddled.
- **Empty-data artifacts**: With no saved council/chair models the chips shrink to tiny pills; endpoint can render as a lone dot. Needs an explicit “using defaults from config.py” message or a populated list.
- **Spacing/whitespace issues**: Large blank area below the buttons and tight spacing above the dashed box; overall vertical rhythm feels uneven. The card padding + shadow makes the form feel oversized compared to the sparse content.
- **Back to Chat placement**: Only appears in the top-right; on long pages users must scroll back up. No bottom affordance.
- **Load/Test/Saving states**: While testing runs, there’s no inline spinner on the buttons; success/error text appears but doesn’t reserve space, causing layout jump.
- **Responsiveness**: The preset grid is fixed to 3 columns min 200px; on tablets it will wrap awkwardly and leave large gutters. Buttons side-by-side may wrap unevenly on narrow viewports.
- **Contrast/focus**: Primary/secondary buttons lose clear focus indication; alerts and labels meet contrast, but focus rings are default and hard to see on light backgrounds.

## Chat surface
- **Full-width reading strain**: Messages and stage cards stretch nearly the full viewport width, making paragraphs hard to scan on large monitors. No max-width or centered column.
- **Message alignment/labeling**: User and assistant messages share similar neutral tones; the “LLM Council” label is small and easily lost in long threads.
- **Scroll positioning**: Smooth scroll on every conversation update can feel jumpy during multi-stage streaming; no sticky headers for context while scrolling long assistant replies.
- **Input area on small screens**: The fixed 24px padding and 80px min-height textarea can force vertical scrolling on short viewports; send button isn’t full-width on mobile.

## Stage views
- **Visual inconsistency across stages**: Stage 1/2 use gray backgrounds; Stage 3 switches to bright green, breaking visual rhythm. Different border treatments and padding per stage.
- **Tabs overflow risk**: Model tabs in Stage 1/2 wrap but lack horizontal scroll; long model names are truncated only by wrapping, which can create multi-line tab buttons.
- **Ranking readability**: Parsed ranking list uses dense monospace with minimal spacing; aggregate rankings lack alignment on wide screens.
- **Markdown overflow**: Long code/links inside stage markdown may overflow containers—no specific styling for code blocks or tables.

## Sidebar & navigation
- **Non-responsive layout**: Fixed 260px sidebar + 100vw app means horizontal overflow on small screens; there’s no collapse or mobile breakpoint.
- **Conversation titles**: Long titles aren’t truncated/ellipsized; they can wrap into multiple lines and push metadata down.
- **Active state clarity**: Active conversation uses a light blue fill but the settings button active state looks similar; could confuse which pane is open.

## Feedback, errors, and empty states
- **Global errors**: Settings load error is prominent but offers no guidance or retry; chat send failures only log to console and remove messages silently.
- **Empty data cues**: Council models/chair preset cards don’t explain what defaults will be used; conversation list empty state is terse.
- **Loading skeletons**: Only text “Loading settings…” is shown; no skeleton for preset cards, causing sudden content pop-in.

## Accessibility & interaction
- **Focus visibility**: Buttons and inputs rely on default outlines; focus is faint against light backgrounds. No skip links or landmark roles.
- **Keyboard navigation**: Stage tabs are keyboard focusable, but there’s no aria-selected/aria-controls to convey tab state to screen readers.
- **Form semantics**: Error messages lack `aria-live` announcements; success/error alerts aren’t tied to inputs.

## Visual consistency & theming
- **Mixed backgrounds**: Sidebar uses warm gray, settings uses cool blue-gray, chat uses white—no single theme. Shadows and radii vary across cards.
- **Typography scale**: Headings, labels, and body text use inconsistent sizes/weights; stage headings are small relative to content.
- **Iconography**: No icons for states (loading/error/success), which makes alerts purely color-dependent.
