import { useEffect, useState } from 'react';
import { request, jsonBody } from '../../services/mvpApi';
export default function useComparison(product, variant, profile, preference) {
  const [snapshot, setSnapshot] = useState(null);
  useEffect(() => {
    if (!product || !variant || !profile) return;
    const controller = new AbortController(),
      context = {
        product,
        variant,
        profile,
        preference
      };
    const timer = setTimeout(() => {
      setSnapshot({
        ...context,
        value: null,
        error: '',
        loading: true
      });
      request(`/mvp/produtos/${product.id}/comparar`, {
        ...jsonBody({
          variant_id: variant.id,
          perfil: profile,
          preferencia: preference
        }),
        signal: controller.signal
      }).then(value => {
        if (!controller.signal.aborted) setSnapshot({
          ...context,
          value,
          error: '',
          loading: false
        });
      }).catch(error => {
        if (error.name !== 'AbortError' && !controller.signal.aborted) setSnapshot({
          ...context,
          value: null,
          error: error.message,
          loading: false
        });
      });
    }, 120);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [product, variant, profile, preference]);
  const current = snapshot?.product === product && snapshot?.variant === variant && snapshot?.profile === profile && snapshot?.preference === preference;
  return current ? snapshot : {
    value: null,
    error: '',
    loading: !!(product && variant && profile)
  };
}
