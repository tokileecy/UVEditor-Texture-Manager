# UVEditor-Texture-Manager
Blender-get-node-texture
在blender的UV/Image Editor的Property工具欄中增價一塊UIEditor Texture Manager
目的上是可以在選擇物件下，依定特定的材質顯示相關的texture，避免在全部的texture或material中抓取
 
可以選擇Render模式（只支持BI即Cycles）, Material, 及是否使用node
依據以上規則會在以下顯示texture，另外在BI下不選擇node則從slot中抓取texture
 
另外若有不同的node使用同張texture，則在layout中會有重複的image。
