;; Setup Vertico + Consult + Orderless stack

(use-package project
  :ensure nil ; Built-in, no need to download
  :custom
  (project-vc-extra-root-markers '(".git" ".project")))

;; ====================================================================
;; 1. VERTICO & UI EXTENSIONS (The Helm Replacements)
;; ====================================================================

(use-package vertico
  :ensure t
  :init (vertico-mode 1)
  ;;(vertico-indexed-mode 1)
  ) ; Enable the clean vertical completion list

(use-package orderless
  :ensure t
  :custom
  (completion-styles '(orderless basic))
  (completion-category-defaults nil)
  (completion-category-overrides '((file (styles partial-completion)))))

(use-package marginalia
  :ensure t
  :init
  ;; 核心防御：等到 time-date 加载完毕并污染了函数之后，我们立刻出手拦截
  (with-eval-after-load 'time-date
    (advice-add 'seconds-to-string :around
                (lambda (orig-fun delay &rest args)
                  (condition-case nil
                      ;; 尝试顺应 Marginalia 的心愿，传入所有新参数
                      (apply orig-fun delay args)
                    ;; 如果 time-date.el 强行降级了该函数导致报参数错
                    ;; 我们就吞掉多余参数，只用 1 个参数保底运行，绝对不让 Vertico 崩溃
                    (wrong-number-of-arguments
                     (funcall orig-fun delay))))))
  :config
  (marginalia-mode 1)
  ) ; Shows file sizes, docstrings, etc. in the list

;;(use-package projectile
;;  :ensure t
;;  :init
;;  (projectile-mode 1)
;;  :bind-keymap
;;  ("C-c p" . projectile-command-map))

;; ====================================================================
;; 2. CONSULT (The Helm-Ag / Core Search Replacements)
;; ====================================================================

(use-package consult
  :ensure t
  :bind (;; Buffer
         ("C-x b" . consult-buffer)
         ("M-y"   . consult-yank-pop)      ; Beautiful kill-ring browser

         ;; Searching
         ("C-s"   . consult-line)            ; Single buffer search
         ("M-s m" . consult-line-multi)    ; Serching in all opened buffers
         ("M-s g" . consult-ripgrep)       ; Interactive project-wide grep

         ;; imenu
         ("C-c o" . consult-imenu)
         )
  :init
  ;; Enable live previewing files/buffers as you scroll through choices
  (setq consult-preview-key 'any))

;; ====================================================================
;; 3. PROJECTILE
;; ====================================================================

;; use Vertico/Consult UI
(use-package consult-projectile
  :ensure t
  :after projectile
  :bind (
         :map projectile-command-map
              ;;("p" . consult-projectile-switch-project)
              ("p" . consult-projectile-buffer)
              ("f" . consult-projectile-find-file)
              ("b" . consult-projectile-switch-to-buffer)
         ))


(use-package consult-project-extra
  :ensure t
  :after projectile
  :bind (;; Lists current project files, buffers, and all known projects
         ("C-x C-b" . consult-project-extra-find)
         ))

;; ====================================================================
;; 4. CODE NAVIGATION (The helm-gtags Replacement)
;; ====================================================================

;; Rather than old gtags, the modern stack uses Universal Ctags via Citre.
;; It hooks directly into standard Emacs 'xref' keys (M-. to jump, M-, to pop back).
(use-package citre
  :ensure t
  :init
  (require 'citre-config)
  :bind (("M-." . xref-find-definitions)
         ("M-?" . xref-find-references)))

;; 1. The Core LSP Engine (Built-in since Emacs 29)
(use-package eglot
  :ensure nil ; Built-in
  :hook ((python-mode . eglot-ensure)
         (typescript-ts-mode . eglot-ensure)
         (go-mode . eglot-ensure)) ; Auto-start for these languages
  :bind (:map eglot-mode-map
              ("M-." . xref-find-definitions)
              ("M-?" . xref-find-references)
              ("C-c r" . eglot-rename)))    ; VS Code's F2 symbol rename

;; 2. Visual Breadcrumbs (Like VS Code's top bar)
(use-package breadcrumb
  :ensure t
  :hook (eglot-managed-mode . breadcrumb-local-mode))

(use-package wgrep
  :ensure t
  :custom
  (wgrep-auto-save-buffer t))
;; 核心工作流提示：
;; 1. 用 M-s g (consult-ripgrep) 搜出你要改的变量
;; 2. 在 Vertico 界面按下 C-c C-e (导出到独立 buffer)
;; 3. 按下 C-c C-p 进入编辑模式，直接改代码！
;; 4. 改完按下 C-c C-c 保存，全项目所有相关文件的代码自动全部被修改。

;; 完美替代 Company 的现代代码补全前端
(use-package corfu
  :ensure t
  :init
  (global-corfu-mode 1)
  :custom
  (corfu-auto t)                  ; 自动弹出
  (corfu-auto-delay 0.0)          ; 零延迟
  (corfu-auto-prefix 1)           ; 1个字母就提示
  (corfu-quit-no-match 'separator)) ; 配合 orderless 的空格分割魔法

(provide 'setup-vertico)
