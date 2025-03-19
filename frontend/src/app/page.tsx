// page.tsx - Updated with processing status handling
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url) return;
    
    setIsLoading(true);
    try {
      // Call the API to generate the diagram
      const response = await fetch('http://localhost:8000/generate_diagram', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate diagram');
      }
      
      const data = await response.json();
      
      // Store the diagram code and repository URL in localStorage
      localStorage.setItem('diagramCode', data.diagram_code);
      localStorage.setItem('repoUrl', url); // Store URL for status checks
      
      // Navigate to the graph render page
      router.push('/graphrender');
    } catch (error) {
      console.error('Error generating diagram:', error);
      alert('Failed to generate diagram. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col space-y-4 items-center justify-center h-screen">
      <form onSubmit={handleSubmit} className="w-full max-w-lg flex flex-col space-y-4 items-center">
        <input
          className="border-2 border-gray-300 p-2 w-full"
          type="text"
          placeholder="Enter your GitHub URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="bg-white text-black p-2 w-full"
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Submit'}
        </button>
      </form>
    </div>
  );
}
