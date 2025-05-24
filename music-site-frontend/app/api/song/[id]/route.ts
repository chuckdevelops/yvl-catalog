import { NextRequest, NextResponse } from 'next/server';

// The Django server URL
const DJANGO_SERVER_URL = process.env.DJANGO_SERVER_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = params.id;
    
    // Validate that ID is a number
    if (!id || isNaN(Number(id))) {
      return new NextResponse(JSON.stringify({ error: 'Invalid song ID' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Fetch data from Django API
    const response = await fetch(`${DJANGO_SERVER_URL}/api_song_detail/${id}/`, {
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
    console.error(`Error in API route /api/song/[id]:`, error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
} 