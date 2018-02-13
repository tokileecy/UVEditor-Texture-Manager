# UVEditor-Texture-Manager
Blender-UVEditor-Texture-Manager 可以只顯示與物件相關的texture，減少查找texture的時間。

僅支持BI與Cycles。

開啟AutoUpdate，在物件、材質、第一張貼圖更動時，會自動更新UVEditor為第一張貼圖。
（slot時為最上面一張，node時為第一個建立的texture node中的貼圖，不存在的情況則為None）
