// Casca do app: em telas menores a barra lateral escura vira gaveta, aberta pelo botão de menu.
(function () {
    function setupSidebarToggle() {
        const btn = document.getElementById('agMenuBtn');
        const scrim = document.getElementById('agScrim');
        if (!btn || !scrim) return;
        const setOpen = open => {
            document.body.classList.toggle('ag-side-open', open);
            btn.setAttribute('aria-expanded', String(open));
            scrim.hidden = !open;
        };
        btn.addEventListener('click', () => setOpen(!document.body.classList.contains('ag-side-open')));
        scrim.addEventListener('click', () => setOpen(false));
        document.addEventListener('keydown', e => { if (e.key === 'Escape') setOpen(false); });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setupSidebarToggle);
    else setupSidebarToggle();
})();
