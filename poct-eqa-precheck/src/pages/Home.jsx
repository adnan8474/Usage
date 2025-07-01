import React from 'react';

export default function Home({ onLaunch }) {
  return (
    <div className="text-center space-y-4 mt-20">
      <h1 className="text-4xl font-bold">Get Ahead of EQA Failures.</h1>
      <p className="text-lg">Upload your EQA results and analyse before submitting.</p>
      <button
        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        onClick={onLaunch}
      >
        Launch Dashboard
      </button>
    </div>
  );
}
