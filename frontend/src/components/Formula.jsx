import { useMemo } from 'react'
import katex from 'katex'

export default function Formula({ math, block = false }) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(math, {
        displayMode: block,
        throwOnError: false,
      })
    } catch {
      return math
    }
  }, [math, block])

  return (
    <span
      className={block ? 'formula-block' : 'formula-inline'}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
