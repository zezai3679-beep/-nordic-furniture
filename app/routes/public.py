from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(tags=["public"])

HTML_FILE = Path(__file__).resolve().parent.parent.parent / "Nordic Furniture Exhibition.html"

INJECT = r"""<script>
(function(){
    var f=document.getElementById("intentForm");
    if(!f)return;
    f.addEventListener("submit",function(e){
        e.stopImmediatePropagation();
        e.preventDefault();
        var ok=true;
        f.querySelectorAll("[required]").forEach(function(el){
            var err=el.parentElement.querySelector(".error-msg");
            if(!el.value.trim()){el.classList.add("error");if(err)err.textContent="此项为必填";ok=false;}
            else{el.classList.remove("error");if(err)err.textContent="";}
        });
        var ph=f.querySelector("#phone");
        if(ph&&ph.value&&!/^[\d\-+\s()]{7,}$/.test(ph.value)){ph.classList.add("error");ph.parentElement.querySelector(".error-msg").textContent="请输入有效的电话号码";ok=false;}
        if(!ok)return;
        var b=f.querySelector(".submit-btn");b.disabled=true;b.textContent="提交中...";
        fetch("/submit",{method:"POST",body:new FormData(f)}).then(function(r){
            if(r.redirected){f.style.display="none";document.getElementById("successMsg").classList.add("show")}
            else{b.disabled=false;b.textContent="提交意向"}
        }).catch(function(){b.disabled=false;b.textContent="提交意向"});
    });
})();
</script>"""


@router.get("/", response_class=HTMLResponse)
async def product_page(request: Request, success: int = 0):
    html = HTML_FILE.read_text(encoding="utf-8")
    html = html.replace("</body>", INJECT + "</body>")
    if success:
        html = html.replace(
            '<form id="intentForm" novalidate>',
            '<div class="success-message show"><h3>提交成功</h3><p>感谢您的关注，我们的顾问将尽快与您联系。</p></div><form id="intentForm" novalidate style="display:none">',
        )
    return html


@router.post("/submit")
async def submit_inquiry(
    request: Request,
    customer_name: str = Form(...),
    contact_name: str = Form(...),
    phone: str = Form(...),
    source: str = Form(""),
    notes: str = Form(""),
):
    payload = {
        "customer_name": customer_name.strip(),
        "contact_name": contact_name.strip(),
        "phone": phone.strip(),
        "source": source.strip(),
        "notes": notes.strip(),
    }
    try:
        await request.app.state.repository.submit_lead(payload)
    except Exception:
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/?success=1", status_code=303)
