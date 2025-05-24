import { NextRequest, NextResponse } from 'next/server';

// The Django server URL
const DJANGO_SERVER_URL = process.env.DJANGO_SERVER_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    // Get query parameters from the request
    const url = new URL(request.url);
    const searchParams = url.searchParams;
    
    // Create URL to Django API with all the query parameters
    const djangoUrl = new URL(`${DJANGO_SERVER_URL}/api_songs/`);
    searchParams.forEach((value, key) => {
      djangoUrl.searchParams.append(key, value);
    });

    // Fetch data from Django API
    const response = await fetch(djangoUrl.toString(), {
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
    console.error('Error in API route /api/songs:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
} 