import { NextResponse } from 'next/server';

// The Django server URL
const DJANGO_SERVER_URL = process.env.DJANGO_SERVER_URL || 'http://localhost:8000';

export async function GET() {
  try {
    // Fetch data from Django API
    const response = await fetch(`${DJANGO_SERVER_URL}/api_home/`, {
      // Include this to forward cookies and authorization headers
      next: { revalidate: 60 }, // Revalidate cache every 60 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      return new NextResponse(JSON.stringify({ error: 'Failed to fetch data from Django' }), {
        status: response.status,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const data = await response.json();
    
    // Return the data from the Django API
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in API route /api/home:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
} 