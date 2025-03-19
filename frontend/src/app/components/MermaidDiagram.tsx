// components/MermaidDiagram.tsx
'use client';

import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  code: string;
}

export default function MermaidDiagram({ code }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && code) {
      try {
        // Initialize mermaid
        mermaid.initialize({
          startOnLoad: true,
          theme: 'default',
        });
        
        // Clear previous diagram
        containerRef.current.innerHTML = '';
        
        // Create a unique ID for this diagram
        const id = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
        
        // Create a div for mermaid to render into
        const element = document.createElement('div');
        element.id = id;
        element.className = 'mermaid';
        element.textContent = code;
        
        // Append the div to our container
        containerRef.current.appendChild(element);
        
        // Render the diagram
        mermaid.contentLoaded();
      } catch (error) {
        console.error('Failed to render mermaid diagram:', error);
        if (containerRef.current) {
          containerRef.current.innerHTML = `<pre>${code}</pre>`;
        }
      }
    }
  }, [code]);

  return <div ref={containerRef} className="w-full h-full"></div>;
}
