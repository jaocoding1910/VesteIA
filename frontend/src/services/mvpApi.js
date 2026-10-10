import { API_BASE_URL } from './apiConfig'
const tokens=new Map()
export function registerCapture(id,token){tokens.set(id,token)}
export function captureHeaders(id){return {Authorization:`Bearer ${tokens.get(id)||''}`}}
export async function request(path,{signal,...options}={}){
  let response
  try{response=await fetch(`${API_BASE_URL}${path}`,{...options,signal,headers:{Accept:'application/json',...options.headers}})}
  catch(error){if(error.name==='AbortError')throw error;throw new Error('Não foi possível conectar à API. Confira se o backend está ligado.',{cause:error})}
  if(response.status===204)return null
  const data=await response.json().catch(()=>null)
  if(!response.ok){const detail=data?.detail;throw new Error(typeof detail==='string'?detail:'Não foi possível concluir. Confira os dados e tente novamente.')}
  return data
}
export const jsonBody=data=>({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
