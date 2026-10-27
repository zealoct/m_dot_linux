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
  :hook (after-init . vertico-mode)
  :config
  (use-package vertico-directory
    :ensure nil ; 内置在 vertico 包中，无需重复下载
    :bind (:map vertico-map
                ;; 快速回退一级目录
                ("C-l" . vertico-directory-up)
                ("RET" . vertico-directory-enter)
                ("DEL" . vertico-directory-delete-char))
    :hook (rfn-eshadow-update-overlay . vertico-directory-tidy)
    )
  ) ; Enable the clean vertical completion list

(use-package orderless
  :ensure t
  :after vertico
  :custom
  (completion-styles '(orderless basic))
  (completion-category-defaults nil)
  (completion-category-overrides '((file (styles partial-completion)))))

(use-package marginalia
  :ensure t
  :after vertico
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
  :config (setq consult-imenu-config
                '((?f "Function"   . font-lock-function-name-face)
                  (?c "Class"      . font-lock-type-face)
                  (?m "Method"     . font-lock-function-name-face)
                  (?v "Variable"   . font-lock-variable-name-face)
                  (?t "Type"       . font-lock-type-face)))

  ;; Enable live previewing files/buffers as you scroll through choices
  (setq consult-preview-key 'any))

;; ====================================================================
;; 3. PROJECTILE
;; ====================================================================

(use-package projectile
  :ensure t
  :bind-keymap ("C-c p" . projectile-command-map)
  :hook (after-init . projectile-mode)
  :config
  (setq projectile-enable-caching t))

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
  :defer t
  :hook (after-init . (lambda () (require 'citre-config)))
  :bind (("M-." . xref-find-definitions)
         ("M-?" . xref-find-references)))

;; 1. The Core LSP Engine (Built-in since Emacs 29)
(use-package eglot
  :ensure nil ; Built-in
  :hook ((c-mode . eglot-ensure)
         (c++-mode . eglot-ensure)
         (cuda-mode . eglot-ensure)
         (python-mode . eglot-ensure)
         (rust-mode . eglot-ensure)
         (typescript-ts-mode . eglot-ensure)
         (go-mode . eglot-ensure)) ; Auto-start for these languages
  :bind (:map eglot-mode-map
              ("M-." . xref-find-definitions)
              ("M-?" . xref-find-references)
              ("C-c r" . eglot-rename))
  :config
  (add-to-list 'eglot-server-programs
               '((cuda-mode :language-id "cuda") . ("clangd")))
  (setq eglot-imenu-config
        '((:Variable nil)      ; 彻底过滤局部变量和全局变量
          (:Field nil)         ; 过滤结构体/类的成员变量（属性）
          (:Constant nil)      ; 过滤常量
          ;; 以下保持默认，允许显示
          (:Class t)
          (:Method t)
          (:Function t)
          (:Interface t)))
  )

(with-eval-after-load 'eglot
  ;; 编写一个深度优先的清洗过滤器，专门用来杀掉嵌套在里面的 Variable
  (defun my/eglot-imenu-clean-variables (entries)
    "深度清理 Imenu 树中的 Variable 和 Field（支持嵌套结构）。"
    (cl-labels ((clean-item (item)
                  (cond
                   ;; 1. 如果是标准的 (Name . Marker) 节点，检查名字或上下文
                   ((atom (cdr item)) t)
                   ;; 2. 如果是一个包含子分类的 (Category . Sub-items) 节点
                   (t
                    (let ((cat (car item)))
                      ;; 如果分类名字叫 Variable, Field, Constant 或 变量，直接整组干掉
                      (if (member cat '("Variable" "Field" "Constant" "变量" "属性"))
                          nil
                        ;; 否则，递归清理它肚子里的子节点
                        (setcdr item (cl-delete-if-not #'clean-item (cdr item)))
                        ;; 如果子节点被清空了，这个分类本身也别留着了
                        (cdr item)))))))
      (cl-delete-if-not #'clean-item entries)))

  ;; 利用 Advice 黑魔法，在 Eglot 生成完 Imenu 准备送给 consult 的瞬间拦截并清洗
  (advice-add 'eglot-imenu :filter-return #'my/eglot-imenu-clean-variables))

;; 2. Visual Breadcrumbs (Like VS Code's top bar)
(use-package breadcrumb
  :ensure t
  :hook (eglot-managed-mode . breadcrumb-local-mode))

(use-package wgrep
  :ensure t
  :defer t
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
  :hook (after-init . global-corfu-mode)
  :custom
  (corfu-auto t)                  ; 自动弹出
  (corfu-auto-delay 0.0)          ; 零延迟
  (corfu-auto-prefix 1)           ; 1个字母就提示
  (corfu-quit-no-match 'separator)) ; 配合 orderless 的空格分割魔法

;; ====================================================================
;; 5. SYMBOL HIGHLIGHTING
;; ====================================================================

;; C-c C-m 高亮 / 取消高亮当前光标下 symbol; 首次调用自动加载 hi-lock
(defun jpt-toggle-mark-word-at-point ()
  (interactive)
  (require 'hi-lock)
  (if hi-lock-interactive-patterns
      (unhighlight-regexp (car (car hi-lock-interactive-patterns)))
    (highlight-symbol-at-point)))
(global-set-key (kbd "C-c C-m") 'jpt-toggle-mark-word-at-point)

(use-package auto-highlight-symbol
  :ensure t
  :hook (after-init . global-auto-highlight-symbol-mode)
  :bind (:map auto-highlight-symbol-mode-map
              ("M-p" . ahs-backward)
              ("M-n" . ahs-forward))
  :config
  (setq ahs-idle-interval 0.3))

;; ====================================================================
;; 6. FILE EXPLORER (dired + dired-subtree, lightweight)
;; ====================================================================
;; F8 在当前 buffer 打开 dired (定位到当前文件所在目录);
;; RET 目录/文件都在当前 buffer 打开 (dired-kill-when-opening-new-dired-buffer
;;   自动关掉旧 dired buffer, 不留一堆);
;; TAB 就地展开/折叠子目录成缩进树 (dired-subtree);
;; <backtab> (Shift-TAB) 循环展开/折叠状态;
;; ^ 上一级; q 退出.

(use-package dired
  :ensure nil ; built-in
  :custom
  (dired-kill-when-opening-new-dired-buffer t) ; Emacs 28+ 内置版 dired-single
  :hook (dired-mode . dired-hide-details-mode)) ; 隐藏 ls -l 那些细节

(use-package dired-subtree
  :ensure t
  :after dired  ; 等 dired load 后
  :demand t     ; 立即 load 自己 (覆盖 :bind 的隐式 defer), 保证 TAB 绑定即时生效
  :custom
  (dired-subtree-use-backgrounds nil) ; 不给每层加深浅不同的背景色 (跟主题冲突时难看)
  (dired-subtree-line-prefix " │  ")  ; 每层加一条竖线, 辅助分辨嵌套层级
  :bind (:map dired-mode-map
              ("TAB"       . dired-subtree-toggle)
              ("<backtab>" . dired-subtree-cycle)             ; Shift-TAB
              ("M-d"       . dired-subtree-remove)            ; 从子树内任意位置折叠父目录
              ("M-n"       . dired-subtree-next-sibling)      ; 下一个兄弟
              ("M-p"       . dired-subtree-previous-sibling)  ; 上一个兄弟
              ("M-u"       . dired-subtree-up)                ; 上级目录
              ))

(provide 'setup-vertico)
