import {useEffect,useRef} from 'react'
import Icon from './Icon'
export default function Modal({title,onClose,children}){
 const ref=useRef(null)
 useEffect(()=>{const dialog=ref.current;dialog.showModal();const cancel=event=>{event.preventDefault();onClose()};dialog.addEventListener('cancel',cancel);return()=>{dialog.removeEventListener('cancel',cancel);dialog.close()}},[onClose])
 return <dialog ref={ref} className="modal" aria-label={title} onClick={event=>{if(event.target===event.currentTarget)onClose()}}><div className="modal-heading"><h2>{title}</h2><button className="icon-button" aria-label="Fechar" onClick={onClose}><Icon name="close"/></button></div>{children}</dialog>
}
