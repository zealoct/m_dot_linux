;; Eval this in your running Emacs (M-x eval-buffer).
;; Lists every single-chord C-/M- binding active in the global map
;; into a buffer named *single-chord-keys*.

(require 'cl-lib)

(defun my/single-chord-binding-p (key)
  "Non-nil if KEY is a single chord carrying a C- or M- modifier
and exactly one non-modifier key (no prefix sequence)."
  (let ((vec (if (vectorp key) key (vector key))))
    (and (= (length vec) 1)
         (let* ((ev  (aref vec 0))
                (mods (event-modifiers ev))
                (base (event-basic-type ev)))
           (and base
                (not (memq 'shift mods))      ; ignore pure S- (windmove)
                (or (memq 'control mods)
                    (memq 'meta   mods)))))))

(defun my/list-single-chord-bindings ()
  (let (out)
    (map-keymap
     (lambda (key def)
       (when (and (my/single-chord-binding-p key)
                  (commandp def))
         (push (cons key def) out)))
     global-map)
    out))

(let* ((bindings (my/list-single-chord-bindings))
       (sorted   (sort bindings
                       (lambda (a b)
                         (string< (key-description (vector (car a)))
                                  (key-description (vector (car b)))))))
       (buf      (get-buffer-create "*single-chord-keys*")))
  (with-current-buffer buf
    (erase-buffer)
    (dolist (b sorted)
      (insert (format "%-12s %s\n"
                      (key-description (vector (car b)))
                      (if (symbolp (cdr b)) (cdr b) "anonymous")))
      ))
  (display-buffer buf)
  (message "Total single-chord C-/M- bindings: %d" (length sorted)))
