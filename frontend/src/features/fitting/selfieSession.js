// Memória desta aba: não grava selfies em localStorage, banco ou disco.
import {useSyncExternalStore} from 'react';
let value=null;
const listeners=new Set();
export function saveSelfieAvatar(next){value=next;listeners.forEach(listener=>listener());}
export function useSelfieAvatar(){return useSyncExternalStore(listener=>{listeners.add(listener);return()=>listeners.delete(listener);},()=>value,()=>null);}
