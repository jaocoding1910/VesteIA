import {addToLook,toggleLook} from '../fitting/lookRules';
import { createContext, useContext, useReducer, useEffect } from 'react';
const Context = createContext(null);
const initial = {
  profile: null,
  profileId: null,
  favorites: [],
  cart: [],
  look: []
};
function load() {
  try {
    const value = JSON.parse(localStorage.getItem('vesteia:mvp:2'));
    return value && Array.isArray(value.cart) && Array.isArray(value.favorites) ? {
      ...initial,
      ...value
    } : initial;
  } catch {
    return initial;
  }
}
function reducer(state, action) {
  switch (action.type) {
    case 'PROFILE':
      return {
        ...state,
        profile: action.profile,
        profileId: action.id || state.profileId || crypto.randomUUID()
      };
    case 'FAVORITE':
      return {
        ...state,
        favorites: state.favorites.includes(action.id) ? state.favorites.filter(id => id !== action.id) : [...state.favorites, action.id]
      };
    case 'ADD':
      {
        const found = state.cart.find(i => i.size_id === action.item.size_id);
        return {
          ...state,
          cart: found ? state.cart.map(i => i.size_id === action.item.size_id ? {
            ...i,
            quantidade: Math.min(99, i.quantidade + 1)
          } : i) : [...state.cart, {
            ...action.item,
            quantidade: 1
          }]
        };
      }
    case 'QUANTITY':
      return {
        ...state,
        cart: state.cart.map(i => i.size_id === action.id ? {
          ...i,
          quantidade: action.quantidade
        } : i).filter(i => i.quantidade > 0)
      };
    case 'CATALOG': {
      const look = state.look.flatMap(item => {
        const product = action.products.find(p => p.id === item.product.id);
        const variant = product?.variantes.find(v => v.sku === item.variant.sku || v.id === item.variant.id);
        const size = variant?.tamanhos.find(s => s.id === item.size.id || s.label === item.size.label);
        return product && variant && size ? [{...item,product,variant,size}] : [];
      });
      return {...state,look};
    }
    case 'LOOK':
      return {
        ...state,
        look: addToLook(state.look,action.item)
      };
    case 'LOOK_SIZE':
      return {
        ...state,
        look: state.look.map(i => i.product.id === action.id ? {
          ...i,
          size: action.size
        } : i)
      };
    case 'LOOK_FIT':
      return {
        ...state,
        look: state.look.map(i => i.product.id === action.id ? {
          ...i,
          fit: action.fit
        } : i)
      };
    case 'TOGGLE_LOOK':
      return {
        ...state,
        look: toggleLook(state.look,action.id)
      };
    case 'REMOVE_LOOK':
      return {
        ...state,
        look: state.look.filter(i => i.product.id !== action.id)
      };
    case 'RESET':
      return initial;
    default:
      return state;
  }
}
export function StoreProvider({
  children
}) {
  const [state, dispatch] = useReducer(reducer, null, load);
  useEffect(() => {
    try {
      localStorage.setItem('vesteia:mvp:2', JSON.stringify(state));
    } catch {/* Navegação continua quando o armazenamento está bloqueado. */}
  }, [state]);
  return <Context.Provider value={{
    state,
    dispatch
  }}>{children}</Context.Provider>;
}
export function useStore() {
  return useContext(Context);
}
