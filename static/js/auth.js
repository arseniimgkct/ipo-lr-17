;(function () {
    function applyPhoneMask(input) {
        if (!input) return
        let digits = input.value.replace(/\D/g, '')

        if (digits.startsWith('375') && digits.length > 3) {
            const d = digits.slice(0, 12)
            let out = '+375'
            if (d.length > 3) out += ' (' + d.slice(3, 5)
            if (d.length >= 5) out += ') ' + d.slice(5, 8)
            if (d.length >= 8) out += '-' + d.slice(8, 10)
            if (d.length >= 10) out += '-' + d.slice(10, 12)
            input.value = out
            return
        }

        if (digits.startsWith('8') && digits.length > 1) {
            const d = ('7' + digits.slice(1)).slice(0, 11)
            let out = '+7'
            if (d.length > 1) out += ' (' + d.slice(1, 4)
            if (d.length >= 4) out += ') ' + d.slice(4, 7)
            if (d.length >= 7) out += '-' + d.slice(7, 9)
            if (d.length >= 9) out += '-' + d.slice(9, 11)
            input.value = out
            return
        }

        if (digits.length === 0) {
            input.value = ''
            return
        }

        let out = '+' + digits.slice(0, 16)
        input.value = out
    }

    function applyIndexMask(input) {
        if (!input) return
        input.value = input.value.replace(/\D/g, '').slice(0, 10)
    }

    function bindPhoneMasks(scope) {
        ;(scope || document)
            .querySelectorAll('[data-phone-input]')
            .forEach(function (input) {
                input.addEventListener('input', function () {
                    applyPhoneMask(input)
                })
                input.addEventListener('focus', function () {
                    if (!input.value) {
                        input.value = '+'
                    }
                })
                input.addEventListener('blur', function () {
                    if (input.value === '+') {
                        input.value = ''
                    }
                })
            })
        ;(scope || document)
            .querySelectorAll('[data-index-input]')
            .forEach(function (input) {
                input.addEventListener('input', function () {
                    applyIndexMask(input)
                })
            })
    }

    function bindPasswordToggles(scope) {
        ;(scope || document)
            .querySelectorAll('[data-toggle-password]')
            .forEach(function (btn) {
                btn.addEventListener('click', function () {
                    const targetId = btn.getAttribute('data-target')
                    const input = document.getElementById(targetId)
                    if (!input) return
                    const isPassword = input.type === 'password'
                    input.type = isPassword ? 'text' : 'password'
                    btn.classList.toggle('is-active', isPassword)
                    btn.setAttribute(
                        'aria-label',
                        isPassword ? 'Скрыть пароль' : 'Показать пароль',
                    )
                })
            })
    }

    function bindStrength() {
        const pw = document.getElementById('id_password1')
        const pw2 = document.getElementById('id_password2')
        if (!pw) return
        const meter = document.createElement('div')
        meter.className = 'auth-strength'
        meter.innerHTML =
            '<span class="auth-strength__bar"><span></span></span><span class="auth-strength__label">Надёжность</span>'
        pw.parentElement.parentElement.appendChild(meter)

        function score(value) {
            let s = 0
            if (value.length >= 8) s++
            if (value.length >= 12) s++
            if (/[A-Z]/.test(value)) s++
            if (/[0-9]/.test(value)) s++
            if (/[^A-Za-z0-9]/.test(value)) s++
            return s
        }

        function paint() {
            const s = score(pw.value)
            const bar = meter.querySelector('.auth-strength__bar > span')
            const label = meter.querySelector('.auth-strength__label')
            const text = ['очень слабый', 'слабый', 'средний', 'хороший', 'отличный']
            const tones = ['tone-1', 'tone-2', 'tone-3', 'tone-4', 'tone-5']
            meter.classList.remove('tone-1', 'tone-2', 'tone-3', 'tone-4', 'tone-5')
            meter.classList.add(tones[Math.min(s, 4)])
            bar.style.width = (Math.min(s, 4) * 25 + 8) + '%'
            label.textContent = pw.value ? text[Math.min(s, 4)] : 'Надёжность'
            if (pw2 && pw2.value) {
                const match = pw.value === pw2.value && pw.value.length > 0
                pw2.parentElement.classList.toggle('is-match', match)
                pw2.parentElement.classList.toggle('is-mismatch', !match)
            }
        }
        pw.addEventListener('input', paint)
        if (pw2) pw2.addEventListener('input', paint)
        paint()
    }

    function bindSubmitAnimation() {
        document
            .querySelectorAll('[data-auth-form]')
            .forEach(function (form) {
                form.addEventListener('submit', function () {
                    const btn = form.querySelector('.auth-submit')
                    if (!btn) return
                    btn.classList.add('is-loading')
                    btn.disabled = true
                })
            })
    }

    document.addEventListener('DOMContentLoaded', function () {
        bindPhoneMasks()
        bindPasswordToggles()
        bindStrength()
        bindSubmitAnimation()
    })
})()
