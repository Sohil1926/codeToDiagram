// app/graphrender/page.tsx
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import MermaidDiagram from '@/app/components/MermaidDiagram';

export default function GraphRender() {
  const [diagramCode, setDiagramCode] = useState<string>('');
  const [question, setQuestion] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    // Get the diagram code from localStorage
    const code = localStorage.getItem('diagramCode');
    if (code) {
      setDiagramCode(code);
    }
  }, []);

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question) return;
    
    setIsLoading(true);
    try {
      // Call the API to generate a new diagram based on the question
      const response = await fetch('http://localhost:8000/ask_question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to process question');
      }
      
      const data = await response.json();
      setDiagramCode(data.diagram_code);
    } catch (error) {
      console.error('Error processing question:', error);
      alert('Failed to process your question. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col space-y-4 items-center justify-center h-screen p-4">
      <div className="w-full max-w-[80vh] h-[80vh] border-2 border-gray-300 flex items-center justify-center overflow-auto">
        {diagramCode ? (
          <MermaidDiagram code={diagramCode} />
        ) : (
          <p className="text-gray-400">Diagram will appear here</p>
        )}
      </div>
      
      <form onSubmit={handleAskQuestion} className="w-full max-w-[80vh] flex flex-col space-y-2">
        <input
          className="w-full border-2 border-gray-300 p-2"
          type="text"
          placeholder="Enter your question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="bg-white text-black p-2 w-full hover:cursor-pointer"
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Ask'}
        </button>
      </form>
      
      <Link href="/" className="text-blue-500 hover:underline">
        Back to Home
      </Link>
    </div>
  );
}
