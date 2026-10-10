import { useEffect, useState, useCallback } from 'react';
import { request } from '../../services/mvpApi';
export default function useCatalog() {
  const [data, setData] = useState([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(''),
    [revision, setRevision] = useState(0);
  const retry = useCallback(() => setRevision(n => n + 1), []);
  useEffect(() => {
    const controller = new AbortController();
    request('/mvp/catalogo', {
      signal: controller.signal
    }).then(value => {
      setData(value.produtos);
      setError('');
    }).catch(e => {
      if (e.name !== 'AbortError') setError(e.message);
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [revision]);
  return {
    data,
    loading,
    error,
    retry
  };
}
