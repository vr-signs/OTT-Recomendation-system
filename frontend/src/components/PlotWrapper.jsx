import React from 'react'
import Plotly from 'plotly.js-dist-min'
import createPlotlyComponent from 'react-plotly.js/factory'
import { useTheme } from '../App.jsx'

const PlotComponent = createPlotlyComponent(Plotly)

export default function PlotWrapper({ data, layout = {}, config = {}, style = {}, ...props }) {
  const { theme } = useTheme()
  const isDark =
    theme === 'Dark' ||
    (theme === 'System' &&
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-color-scheme: dark)').matches)

  const textColor = isDark ? '#d2d2d7' : '#424245'
  const gridColor = isDark ? 'rgba(255,255,255,0.10)' : 'rgba(60,60,67,0.10)'
  const lineColor = isDark ? 'rgba(255,255,255,0.14)' : 'rgba(60,60,67,0.13)'

  const mergedLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: {
      family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
      color: textColor,
      size: 11,
      ...layout.font,
    },
    margin: { t: 30, r: 20, b: 30, l: 20, ...layout.margin },
    xaxis: {
      gridcolor: gridColor,
      linecolor: lineColor,
      zeroline: false,
      ...layout.xaxis,
    },
    yaxis: {
      gridcolor: gridColor,
      linecolor: lineColor,
      zeroline: false,
      ...layout.yaxis,
    },
    ...layout,
  }

  const mergedConfig = {
    displayModeBar: false,
    responsive: true,
    ...config,
  }

  return (
    <PlotComponent
      data={data}
      layout={mergedLayout}
      config={mergedConfig}
      style={{ width: '100%', height: '100%', ...style }}
      useResizeHandler={true}
      {...props}
    />
  )
}
