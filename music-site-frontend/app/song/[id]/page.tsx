import Layout from '../../components/Layout';
import SongDetail from '../../components/SongDetail';

interface SongPageProps {
  params: {
    id: string;
  };
}

export default function SongPage({ params }: SongPageProps) {
  return (
    <Layout>
      <SongDetail songId={Number(params.id)} />
    </Layout>
  );
} 