document.addEventListener('DOMContentLoaded', () => {

    document.querySelector("#addtags").onclick = ()=> {        
        document.querySelectorAll(".products").forEach(r => {
            let n = r.dataset.name;
            let tag = `tags_${n}`;
            if (document.getElementById(tag)) {
                r.style.display = "none";
            } else {
                r.style.display = "block";
            }
        });
        return false;
    };

    document.querySelector("#return_addtags").onclick = ()=> {
        document.querySelectorAll(".products").forEach(r => {
            r.style.display = "block";
        });
        return false;
    };    
});