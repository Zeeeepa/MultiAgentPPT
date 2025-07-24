# 记录生成的原理
Main.tsx -> PresentationSlidesView.tsx (遍历Slides) -> SlideContainer.tsx (渲染单张Slide) ->
  presentation-editor.tsx (使用富文本编辑框架，根据数据渲染标题、图片、自定义图表等具体内容)。

# nextjs调用本机api生成内容
http://localhost:3000/api/presentation/generate

# DetailPanel.tsx的逻辑
1.显示处理中每个Agent的进度，首先src/app/api/presentation/generate/route.ts返回的数据包含metadata和type,并且是流式的返回Json的数据。
2. src/components/presentation/dashboard/PresentationGenerationManager.tsx 写新的函数，generatePresentationStream解析返回的数据const { type, data, metadata } = JSON.parse(line);
3. 根据不同的type类型，判断是否放到setDetailLogs还是parser.parseChunk(data);对xml格式进行解析。
4. DetailLogs数据通过zustand的usePresentationState保存，然后在src/components/presentation/presentation-page/Main.tsx中使用

## 根据图片是否是背景图片对图片进行展示, 背景图片，那么样式是object-cover，如果不是背景图片，那么样式是contain，即缩放显示，显示全图
src/components/presentation/editor/native-elements/root-image.tsx
                <PopoverTrigger asChild>
                  <div
                    className="relative h-full"
                    tabIndex={0}
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowDeletePopover(true);
                    }}
                    onDoubleClick={handleImageDoubleClick}
                  >
                    {/*  eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={imageUrl ?? image.url}
                      alt={image.alt}
                      className={`h-full w-full ${image.background ? "object-cover" : "object-contain"}`}
                      style={{
                        height: image.background !== true && image.alt ? "calc(100% - 32px)" : "100%",
                        // 32px 用于说明文字实际高度调整
                      }}
                      onError={(e) => {
                        console.error(
                          "Image failed to load:",
                          e,
                          imageUrl ?? image.url
                        );
                        // Optionally set a fallback image or show an error state
                      }}  
                    />
                    {/* 非背景图片时显示说明文字 */}
                    {image.background !== true && image.alt && (
                      <div
                        style={{
                          position: "absolute",
                          left: "50%",
                          bottom: 0,
                          transform: "translateX(-50%)",
                          background: "rgba(0,0,0,0.6)",
                          color: "#fff",
                          padding: "2px 8px",
                          borderRadius: "6px 6px 0 0",
                          fontSize: "0.85rem",
                          whiteSpace: "pre-line",
                          maxWidth: "90%",
                          textAlign: "center",
                        }}
                      >
                        {image.alt}
                      </div>
                    )}
                  </div>
                </PopoverTrigger>


## PPT页的唯一性，避免遗漏和重复，目前是使用的generateSectionIdentifier函数，使用的是h1Node的内容作为key，我们新加大模型输出<SECTION layout="left" | "right" | "vertical" page_number=x>，page_number作为唯一key，那样可以覆盖已有PPT，方便PPT_checker更新PPT内容
  private generateSectionIdentifier(sectionNode: XMLNode): string {
    // 优先使用 page_number 作为唯一标识
    if (sectionNode.attributes && sectionNode.attributes.page_number) {
      return `page_number-${sectionNode.attributes.page_number}`;
    }

## 图片加载失败后不显示，防止模型幻觉
src/components/presentation/editor/native-elements/root-image.tsx
  const [imageLoadFailed, setImageLoadFailed] = useState(false);

  if (imageLoadFailed) {
    return null;
  }

## 下载PPT按钮
src/components/presentation/presentation-page/PresentationHeader.tsx
Buttons目录下添加DownloadPPT.tsx
src/components/presentation/presentation-page/buttons
.env添加下载环境变量
DOWNLOAD_SLIDES_URL="http://localhost:10021"
后端API：src/app/api/presentation/download/route.ts
功能：接收前端传来的items（即所有幻灯片内容），调用后端PPT生成服务（读取DOWNLOAD_SLIDES_URL环境变量），返回PPT下载链接。
实现要点：
POST请求，body为{ items }。
读取process.env.DOWNLOAD_SLIDES_URL。
调用后端服务，获取PPT下载链接，返回给前端。
2. 前端按钮组件：src/components/presentation/presentation-page/buttons/DownloadPPT.tsx
功能：点击后自动将当前所有items（通过usePresentationSlides获取）POST到API，收到下载链接后自动下载PPT。
实现要点：
使用Button组件，风格与ShareButton一致。
使用lucide-react的Download图标。
点击后禁用按钮并显示loading，防止重复点击。
成功后自动触发浏览器下载。
3. 在Header中集成
功能：在PresentationHeader.tsx右侧按钮区，ShareButton旁边插入DownloadPPT按钮，仅在isPresentationPage且未在放映状态下显示。

# 去除裁剪，否则显示不全
src/components/presentation/dashboard/PresentationDashboard.tsx

去除裁剪
        presentationInput.substring(0, 50) || "Untitled Presentation"


      const result = await createEmptyPresentation(
        presentationInput || "Untitled Presentation"
      );
