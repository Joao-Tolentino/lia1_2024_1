import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import pyautogui
import mediapipe

face_mesh = mediapipe.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

class QwertyKeyboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assistente")
        self.root.attributes('-fullscreen', True)

        # Parar o programa ao apertar Esc
        self.root.bind('<Escape>', self.close_window2)

        # QWERTY keyboard layout
        self.keyboard_layout = [
            ['Delete', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '+', '=', '<--'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\', '@'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ç', ',', '.', ';', '/'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'Espaço'],
        ]

        # Inicializa o OpenCV para camera
        self.cap = cv2.VideoCapture(0)  # Usa camera default

        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot open webcam.")

        # Cria caixa de texto de input (no topo)
        self.entry = tk.Entry(self.root, font=('Arial', 24))
        self.entry.grid(row=0, column=0, columnspan=len(self.keyboard_layout[0]), sticky='nsew', padx=10, pady=10)

        # Adiciona o texto "Use Esc para sair"
        self.exit_label = tk.Label(self.root, text="Use Esc para sair", font=('Arial', 26), fg='black')
        self.exit_label.grid(row=1, column=0, columnspan=len(self.keyboard_layout[0]), sticky='nsew', padx=10, pady=5)

        # Cria canvas para colocar o feed da camera
        self.canvas = tk.Canvas(self.root)
        self.canvas.grid(row=2, column=0, rowspan=len(self.keyboard_layout) + 1, columnspan=len(self.keyboard_layout[0]), sticky='nsew')
        self.canvas.configure(background='black')

        # Cria um botão de fechar (a frente do feed)
        self.close_button = tk.Button(self.root, text="X", command=self.close_window, width=5, height=3)
        self.close_button.grid(row=2, column=len(self.keyboard_layout[0]), sticky='ne', padx=10, pady=10)

        # Cria botões para o layout dos botões (a frente do feed)
        for row_idx, row in enumerate(self.keyboard_layout):
            for col_idx, letter in enumerate(row):
                button = tk.Button(self.root, text=letter, width=6, height=2, font=('Arial', 14),
                                   command=lambda l=letter: self.button_click(l))
                button.grid(row=row_idx + 3, column=col_idx, padx=5, pady=5)  # Começa da linha 3 para os botões

        # Configura os pesos do grid
        self.root.grid_rowconfigure(0, weight=1)  # linha da entrada
        self.root.grid_rowconfigure(len(self.keyboard_layout) + 3, weight=1)  # linha botões
        for i in range(len(self.keyboard_layout) + 2):
            self.root.grid_rowconfigure(i + 1, weight=1)
        for j in range(len(self.keyboard_layout[0])):
            self.root.grid_columnconfigure(j, weight=1)
        self.root.grid_columnconfigure(len(self.keyboard_layout[0]), weight=1)

        # Move o cursor para o centro da tela uma única vez
        self.j = 0

        # Update do feed da camera (background/fundo)
        self.update_camera()

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            # Remove espelhamento
            frame = cv2.flip(frame, 1)

            # Olho camera
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = face_mesh.process(frame_rgb)
            landmark_points = output.multi_face_landmarks

            frame_h, frame_w, _ = frame.shape  # h->altura<-y // w->largura<-x
            if landmark_points:
                landmarks = landmark_points[0].landmark
                for id, landmark in enumerate(landmarks[474:478]):  # Escolhemos apenas 4 marcações que são do olho direito
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv2.circle(frame, (x, y), 3, (0, 255, 0))
                    if id == 1:
                        screen_x = int(landmark.x * screen_w)
                        screen_y = int(landmark.y * screen_h)

                        # Garantir que as coordenadas estejam dentro dos limites da tela
                        screen_x = min(max(50, screen_x), screen_w - 50)
                        screen_y = min(max(50, screen_y), screen_h - 50)

                        pyautogui.moveTo(screen_x, screen_y)

                Esquerdo = [landmarks[145], landmarks[159]]
                for landmark in Esquerdo:
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv2.circle(frame, (x, y), 3, (255, 0, 0))
                # quando os dois pontos estão próximos então o olho fechou
                if (Esquerdo[0].y - Esquerdo[1].y < 0.009):
                    pyautogui.click()

            # Move o cursor para o centro da tela apenas uma vez
            if self.j == 0:
                pyautogui.moveTo(screen_w // 2, screen_h // 2)
                self.j = -1

            # Altera o tamanho do frame para o tamanho do canvas
            frame = self.resize_frame(frame, self.canvas.winfo_width(), self.canvas.winfo_height())

            # Converte OpenCV BGR frame para RGB e depois para PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            self.photo = ImageTk.PhotoImage(image=image)

            # Update no canvas com a próxima imagem
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Update da camera a cada 10 ms
        self.root.after(10, self.update_camera)

    def resize_frame(self, frame, width, height):
        """Muda o tamanho do frame para especificações."""
        return cv2.resize(frame, (width, height))

    def close_window(self, event=None):
        if messagebox.askokcancel("Fechar", "Você deseja fechar?"):
            self.cap.release()  # Libera o uso da webcam ao fechar
            self.root.destroy()

    def close_window2(self, event=None):
        self.cap.release()  # Libera o uso da webcam ao fechar
        self.root.destroy()

    def button_click(self, key):
        if key == '<--':
            current_text = self.entry.get()
            self.entry.delete(len(current_text) - 1, tk.END)  # Deleta caractere
        elif key == 'Delete':
            self.entry.delete(0, tk.END)  # Limpa entrada
        elif key == 'Espaço':
            self.entry.insert(tk.END, ' ')
        else:
            self.entry.insert(tk.END, key)  # Insere caractere pressionado

if __name__ == "__main__":
    root = tk.Tk()
    app = QwertyKeyboardApp(root)
    root.mainloop()