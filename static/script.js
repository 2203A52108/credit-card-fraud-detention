const form=document.getElementById("form");
form.addEventListener("submit",async(e)=>{
 e.preventDefault();
 const body={
  amount:document.getElementById("amount").value,
  hour:document.getElementById("hour").value,
  distance:document.getElementById("distance").value,
  velocity:document.getElementById("velocity").value,
  international:document.getElementById("international").checked
 };
 const res=await fetch("/predict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
 const d=await res.json();
 document.getElementById("result").textContent=d.prediction;
 document.getElementById("score").textContent=d.fraud_probability+"%";
 document.getElementById("fraud").textContent=d.fraud_probability+"%";
 document.getElementById("legit").textContent=d.legitimate_probability+"%";
 document.getElementById("risk").textContent=d.risk;
 document.getElementById("icon").textContent=d.prediction.startsWith("Fraud")?"!":"✓";
 document.getElementById("note").textContent=d.prediction.startsWith("Fraud")?"This transaction has elevated fraud indicators.":"This transaction currently shows a low fraud risk.";
 const deg=d.fraud_probability*3.6;
 document.getElementById("ring").style.background=`conic-gradient(${d.prediction.startsWith("Fraud")?"#ff667a":"#49d6a4"} ${deg}deg,#172a3e ${deg}deg)`;
});
