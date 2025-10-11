/* storage */
function loadTicketsRaw(){try{return JSON.parse(localStorage.getItem('studentTickets')||'[]')}catch{return[]}}
function saveTickets(list){try{localStorage.setItem('studentTickets',JSON.stringify(list))}catch{}}
function normalizeTickets(list){
  const seen=new Set(), out=[];
  for(const t of list){
    const sig=`${t.name}|${t.date}|${t.organization}`;
    if(seen.has(sig)) continue;
    seen.add(sig);
    out.push({ticketId:t.ticketId||`${Date.now()}-${Math.random().toString(16).slice(2)}`,name:t.name,category:t.category,organization:t.organization,date:t.date,claimedAt:t.claimedAt||new Date().toISOString()});
  }
  return out;
}
function loadTickets(){return normalizeTickets(loadTicketsRaw())}
/* helpers */
function payloadForQR(t){return JSON.stringify({v:1,id:t.ticketId,n:t.name,d:t.date,org:t.organization,ts:t.claimedAt})}
function el(tag,attrs={},children=[]){const e=document.createElement(tag);for(const[k,v]of Object.entries(attrs)){if(k==='class')e.className=v;else if(k==='text')e.textContent=v;else e.setAttribute(k,v)}children.forEach(c=>e.appendChild(c));return e}
/* render */
let active=null;
function render(){
  const grid=document.getElementById('ticketsGrid');const empty=document.getElementById('emptyState');
  let tickets=loadTickets();saveTickets(tickets);
  grid.innerHTML=''; if(!tickets.length){empty.classList.remove('hidden');return} empty.classList.add('hidden');
  tickets.sort((a,b)=>a.claimedAt<b.claimedAt?1:-1);
  tickets.forEach(t=>{
    const card=el('div',{class:'card'});
    card.appendChild(el('h4',{text:t.name}));
    card.appendChild(el('div',{class:'meta',text:`${t.organization} • ${t.date}`}));
    card.appendChild(el('span',{class:'tag',text:`Ticket #${t.ticketId.slice(-6)}`}));
    const qrBox=el('div',{class:'qr'}); card.appendChild(qrBox);
    if(window.QRCode){new QRCode(qrBox,{text:payloadForQR(t),width:140,height:140,correctLevel:QRCode.CorrectLevel.M});}
    else qrBox.textContent='QR library missing';
    const actions=el('div',{class:'card-actions'});
    const viewBtn=el('button',{class:'btn',text:'View QR'});
    const rmBtn=el('button',{class:'btn secondary',text:'Remove'});
    viewBtn.addEventListener('click',()=>openDialog(t));
    rmBtn.addEventListener('click',()=>{const rest=loadTickets().filter(x=>x.ticketId!==t.ticketId);saveTickets(rest);render();});
    actions.appendChild(viewBtn);actions.appendChild(rmBtn);card.appendChild(actions);
    grid.appendChild(card);
  });
}
/* dialog */
const dlg=()=>document.getElementById('qrDialog');
function openDialog(ticket){
  active=ticket; const d=dlg(); const title=document.getElementById('dlgTitle'); const box=document.getElementById('dlgQR');
  title.textContent=ticket.name; box.innerHTML='';
  d.showModal();
  if(window.QRCode){
    new QRCode(box,{text:payloadForQR(ticket),width:260,height:260,correctLevel:QRCode.CorrectLevel.H});
    if(!box.querySelector('canvas,img')) setTimeout(()=>{box.innerHTML=''; new QRCode(box,{text:payloadForQR(ticket),width:260,height:260,correctLevel:QRCode.CorrectLevel.H});},50);
  } else box.textContent='QR library not loaded';
}
function closeDialog(){dlg().close(); active=null;}
function downloadDialogQR(){
  const canvas=document.querySelector('#dlgQR canvas'); const img=document.querySelector('#dlgQR img'); if(!active) return;
  const a=document.createElement('a'); a.download=`ticket-${active.ticketId}.png`; a.href=canvas?canvas.toDataURL('image/png'):(img?img.src:''); if(a.href) a.click();
}
/* boot */
document.addEventListener('DOMContentLoaded',()=>{
  render();
  document.getElementById('dlgClose')?.addEventListener('click',closeDialog);
  document.getElementById('dlgDownload')?.addEventListener('click',downloadDialogQR);
  document.getElementById('qrDialog')?.addEventListener('click',e=>{const body=e.currentTarget.querySelector('.dialog-body'); if(!body.contains(e.target)) closeDialog();});
  document.getElementById('clearBtn')?.addEventListener('click',()=>{if(confirm('Clear all claimed tickets?')){localStorage.removeItem('studentTickets');render();}});
});
