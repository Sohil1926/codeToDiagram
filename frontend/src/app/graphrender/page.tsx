// app/graphrender/page.tsx - Updated with status polling
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import MermaidDiagram from '@/app/components/MermaidDiagram';

export default function GraphRender() {
  const [diagramCode, setDiagramCode] = useState<string>('');
  const [question, setQuestion] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [processingComplete, setProcessingComplete] = useState<boolean>(false);

  useEffect(() => {
    // Get the diagram code from localStorage
    const code = localStorage.getItem('diagramCode');
    const repoUrl = localStorage.getItem('repoUrl');
    
    if (code) {
      setDiagramCode(code);
    }
    
    // Set up polling for processing status if we have a URL
    if (repoUrl) {
// In GraphRender component's checkStatus function
// In GraphRender component's checkStatus function

const checkStatus = async () => {
    try {
      // Call the status endpoint with URL as a query parameter
      const encodedUrl = encodeURIComponent(repoUrl);
      const response = await fetch(`http://localhost:8000/processing_status?url=${encodedUrl}`);
      if (response.ok) {
        const data = await response.json();
        setProcessingStatus(data.status);
        
        // If processing is complete, stop polling
        if (data.status === 'completed') {
          setProcessingComplete(true);
          return true;
        } else if (data.status === 'failed') {
          console.error('Processing failed');
          return true;
        }
      }
      return false;
    } catch (error) {
      console.error('Error checking processing status:', error);
      return false;
    }
  };
  
      
      // Poll every 3 seconds
      const intervalId = setInterval(async () => {
        const shouldStop = await checkStatus();
        if (shouldStop) {
          clearInterval(intervalId);
        }
      }, 3000);
      
      // Clean up interval on component unmount
      return () => clearInterval(intervalId);
    }
  }, []);

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question) return;
    
    // Don't allow asking questions until processing is complete
    if (!processingComplete) {
      alert('Please wait for repository processing to complete before asking questions.');
      return;
    }
    
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
      {/* Processing status indicator */}
      {processingStatus && processingStatus !== 'completed' && (
        <div className="bg-blue-100 text-blue-800 p-2 w-full max-w-[80vh] text-center">
          Repository processing: {processingStatus}
          {!processingComplete && ' (You can view the diagram, but cannot ask questions yet)'}
        </div>
      )}
      
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
          placeholder={processingComplete ? "Enter your question" : "Please wait for processing to complete..."}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isLoading || !processingComplete}
        />
        <button
          type="submit"
          className="bg-white text-black p-2 w-full hover:cursor-pointer"
          disabled={isLoading || !processingComplete}
        >
          {isLoading ? 'Loading...' : processingComplete ? 'Ask' : 'Processing...'}
        </button>
      </form>
      
      <Link href="/" className="text-blue-500 hover:underline">
        Back to Home
      </Link>
    </div>
  );
}
