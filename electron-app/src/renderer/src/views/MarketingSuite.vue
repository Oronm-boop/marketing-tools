<template>
  <div class="suite-shell">
    <aside class="suite-sidebar" aria-label="主导航">
      <div class="suite-brand">
        <img :src="brandLogoUrl" alt="MDT Marketing" />
      </div>

      <nav class="suite-nav" aria-label="营销工具导航">
        <button
          v-for="item in primaryNav"
          :key="item.id"
          class="nav-item"
          :class="{ active: activeNavPage === item.page }"
          type="button"
          :aria-disabled="!item.page"
          @click="item.page && goToPage(item.page)"
        >
          <span class="nav-icon">
            <IconGlyph :name="item.icon" />
          </span>
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <div class="suite-nav nav-secondary">
        <button
          class="nav-item"
          :class="{ active: activeNavPage === 'accounts' }"
          type="button"
          @click="goToPage('accounts')"
        >
          <span class="nav-icon">
            <IconGlyph name="account" />
          </span>
          <span>账号管理</span>
        </button>
        <button class="nav-item" type="button" @click="openSettings">
          <span class="nav-icon">
            <IconGlyph name="settings" />
          </span>
          <span>设置</span>
        </button>
      </div>

      <button class="help-center" type="button" @click="openHelpDialog">
        <span class="nav-icon">
          <IconGlyph name="help" />
        </span>
        <span>帮助</span>
      </button>
    </aside>

    <section class="suite-main">
      <header v-if="showSuiteHeader" class="suite-header">
        <div>
          <h1>{{ headerTitle }}</h1>
          <p>{{ headerSubtitle }}</p>
        </div>
        <div class="header-actions">
          <button v-if="visiblePage !== 'accounts'" class="history-top-button" type="button" @click="openHistory()">
            <IconGlyph name="history" />
            <span>历史记录</span>
          </button>
          <button
            v-if="visiblePage !== 'accounts'"
            class="icon-button"
            type="button"
            aria-label="模型设置"
            @click="openSettings"
          >
            <IconGlyph name="settings" />
          </button>
          <div class="user-avatar" aria-label="用户头像">
            <IconGlyph name="user" />
          </div>
        </div>
      </header>

      <main class="suite-content" :class="`page-${visiblePage}`">
        <section v-if="visiblePage === 'trends'" class="page-stack trends-page">
          <form class="search-bar" @submit.prevent="analyzeTrends">
            <IconGlyph name="search" />
            <input v-model="trendQuery" type="text" placeholder="输入关键词 (例如: 'AI 智能体')" />
            <button type="submit">分析</button>
          </form>

          <div class="dashboard-grid">
            <article class="data-card">
              <div class="card-title-row">
                <span class="card-icon blue"><IconGlyph name="hash" /></span>
                <h2>热门关键词</h2>
              </div>
              <div class="keyword-pills">
                <span v-for="tag in trendKeywords" :key="tag.text" :class="{ selected: tag.selected }">
                  {{ tag.text }}
                </span>
              </div>
            </article>

            <article class="data-card">
              <div class="card-title-row">
                <span class="card-icon red"><IconGlyph name="fire" /></span>
                <h2>爆款内容</h2>
              </div>
              <div class="hot-list">
                <div v-for="item in hotContent" :key="item.title" class="hot-list-item">
                  <span>{{ item.title }}</span>
                  <strong>{{ item.views }}</strong>
                </div>
              </div>
            </article>

            <article class="data-card tall">
              <div class="card-title-row">
                <span class="card-icon gray"><IconGlyph name="chart" /></span>
                <h2>竞品分析</h2>
              </div>
              <div class="competitor-list">
                <div v-for="item in competitors" :key="item.name" class="competitor-item">
                  <span class="competitor-badge">{{ item.short }}</span>
                  <div class="competitor-meta">
                    <div>
                      <span>{{ item.name }}</span>
                      <strong>{{ item.value }}%</strong>
                    </div>
                    <span class="progress-track">
                      <span class="progress-value" :style="{ width: `${item.value}%`, background: item.color }"></span>
                    </span>
                  </div>
                </div>
              </div>
            </article>

            <article class="data-card tall">
              <div class="card-title-row">
                <span class="card-icon green"><IconGlyph name="groups" /></span>
                <h2>目标人群</h2>
              </div>
              <div class="bar-chart" aria-hidden="true">
                <span class="bar bar-1"></span>
                <span class="bar bar-2"></span>
                <span class="bar bar-3"></span>
                <span class="bar bar-4"></span>
              </div>
              <h3 class="minor-heading">用户标签</h3>
              <div class="audience-tags">
                <span v-for="tag in audienceTags" :key="tag">{{ tag }}</span>
              </div>
              <div class="persona-box">
                <span>人群画像简述</span>
                <p>对 AI 效率工具有浓厚兴趣的一线城市专业人士</p>
              </div>
            </article>
          </div>

          <article class="advice-card">
            <div class="advice-title">
              <IconGlyph name="bulb" />
              <h2>AI 营销建议</h2>
            </div>
            <ul>
              <li v-for="item in marketingAdvice" :key="item">
                <IconGlyph name="check" />
                <span>{{ item }}</span>
              </li>
            </ul>
          </article>
        </section>

        <section v-else-if="visiblePage === 'seo'" class="reference-split-page seo-page">
          <aside class="reference-config-panel">
            <header class="panel-title">
              <span class="panel-title-icon"><IconGlyph name="key" /></span>
              <div>
                <h1>关键词生成</h1>
                <p>一键生成SEO关键词</p>
              </div>
            </header>

            <form class="reference-form" @submit.prevent="submitSeo">
              <div class="reference-fields">
                <label class="input-field">
                  <span>我是做什么的</span>
                  <input
                    v-model="seoForm.business"
                    :disabled="seoLoading"
                    type="text"
                    placeholder="例如:高端智能家居设备厂商"
                  />
                </label>
                <label class="input-field">
                  <span>产品特点</span>
                  <textarea
                    v-model="seoForm.features"
                    :disabled="seoLoading"
                    placeholder="描述您的产品核心卖点、竞争优势或目标客群..."
                  ></textarea>
                </label>
                <label class="input-field count-field">
                  <span>关键词数量</span>
                  <input
                    v-model.number="seoForm.keywordCount"
                    :disabled="seoLoading"
                    min="1"
                    max="100"
                    type="number"
                    placeholder="输入1-100"
                  />
                  <em>MAX100</em>
                </label>
                <p v-if="seoError" class="error-text">{{ seoError }}</p>
              </div>
              <footer class="panel-action-bar">
                <button class="primary-action" :disabled="seoLoading" type="submit">
                  <IconGlyph name="spark" />
                  <span>{{ seoLoading ? '生成中...' : '生成SEO关键词' }}</span>
                </button>
              </footer>
            </form>
          </aside>

          <section class="reference-workspace">
            <header class="workspace-header">
              <div>
                <h2>生成结果</h2>
                <p>
                  我是做什么的
                  <strong>「{{ seoForm.business || 'AIPC' }}」</strong>
                </p>
              </div>
              <button class="history-top-button" type="button" @click="openHistory('seo')">
                <IconGlyph name="history" />
                <span>历史记录</span>
              </button>
            </header>

            <div class="workspace-scroll">
              <section class="result-card seo-result-card">
                <div class="result-toolbar">
                  <span></span>
                  <button class="ghost-button compact" type="button" @click="resetSeoResults">
                    <IconGlyph name="refresh" />
                    <span>重新生成</span>
                  </button>
                </div>
                <h3>SEO关键词结果</h3>
                <div v-if="displayedSeoResults.length" class="result-tags">
                  <span v-for="item in displayedSeoResults" :key="item.keyword">{{ item.keyword }}</span>
                </div>
                <div v-else class="seo-empty-state">
                  <IconGlyph name="key" />
                  <strong>这里会生成 SEO 关键词结果</strong>
                  <span>包含关键词、搜索量预估，并可从每条结果继续生成宣传文案</span>
                </div>
                <table v-if="displayedSeoResults.length" class="suite-table">
                  <thead>
                    <tr>
                      <th>关键词</th>
                      <th>搜索量预估</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in displayedSeoResults" :key="`${item.keyword}-${item.search_volume_est}`">
                      <td>{{ item.keyword }}</td>
                      <td>{{ item.search_volume_est }}</td>
                      <td>
                        <button class="link-action" type="button" @click="prepareCopyFromKeyword(item.keyword)">
                          生成宣传文案
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </section>
            </div>
          </section>
        </section>

        <section v-else-if="visiblePage === 'copywriting'" class="reference-split-page copy-page reference-copy-page">
          <form class="copy-settings-card reference-config-panel" @submit.prevent="submitCopy">
            <div class="panel-title">
              <span class="panel-title-icon"><IconGlyph name="document" /></span>
              <div>
                <h1>文案生成</h1>
                <p>一键生成爆款社媒文案</p>
              </div>
            </div>

            <div class="reference-fields copy-reference-fields">
              <label class="input-field">
                <span>核心关键词</span>
                <input
                  v-model="copyForm.keyword"
                  :disabled="copyLoading"
                  type="text"
                  placeholder="例如：AIPC"
                />
              </label>
              <label class="range-field copy-range-field">
                <span>出现次数</span>
                <em>关键词频率</em>
                <strong>{{ copyForm.keywordOccurrences }}</strong>
                <input
                  v-model.number="copyForm.keywordOccurrences"
                  :disabled="copyLoading"
                  type="range"
                  min="0"
                  max="10"
                />
              </label>
              <fieldset class="copy-platform-field">
                <legend>发布平台</legend>
                <div class="copy-platform-options">
                  <label v-for="platform in socialPlatforms" :key="platform" :class="{ checked: copyForm.platform === platform }">
                    <input v-model="copyForm.platform" :disabled="copyLoading" :value="platform" name="copy-platform" type="radio" />
                    <span>{{ platform }}</span>
                  </label>
                </div>
              </fieldset>
              <label class="select-field">
                <span>生成篇数</span>
                <select v-model.number="copyForm.articleCount" :disabled="copyLoading">
                  <option :value="1">1</option>
                  <option :value="3">3</option>
                  <option :value="5">5</option>
                  <option :value="8">8</option>
                </select>
              </label>
              <label class="select-field">
                <span>文案长度</span>
                <select v-model="copyLength" :disabled="copyLoading">
                  <option>中等长度(200-300字)</option>
                  <option>短文案(100-200字)</option>
                  <option>长文案(300-500字)</option>
                </select>
              </label>
              <p v-if="copyError" class="error-text">{{ copyError }}</p>
            </div>

            <div class="panel-action-bar">
              <button class="primary-action" :disabled="copyLoading" type="submit">
                <IconGlyph name="spark" />
                <span>{{ copyLoading ? '生成中...' : '立即生成文案' }}</span>
              </button>
            </div>
          </form>

          <section class="copy-preview-card reference-workspace">
            <header class="workspace-header copy-workspace-header">
              <div>
                <h2>生成结果</h2>
                <p>共 {{ displayedCopyResults.length }} 篇文案 · 关键词「{{ copyForm.keyword || '待输入' }}」</p>
              </div>
              <button class="history-top-button" type="button" @click="openHistory('copy')">
                <IconGlyph name="history" />
                <span>历史记录</span>
              </button>
            </header>

            <div class="workspace-scroll copy-results-scroll">
              <div class="copy-results">
                <div v-if="!displayedCopyResults.length" class="copy-empty-state">
                  <IconGlyph name="message" />
                  <strong>暂无文案内容</strong>
                  <span>生成结果会显示在这里</span>
                </div>
                <article v-for="(item, index) in displayedCopyResults" :key="`${item.title}-${index}`" class="copy-output">
                  <div class="copy-output-head">
                    <div class="copy-output-title-group">
                      <span class="copy-output-index">{{ formatCopyIndex(index) }}</span>
                      <div class="copy-output-meta">
                        <h2>文案方案 {{ index + 1 }}</h2>
                        <span class="copy-platform-badge" :class="getCopyPlatformClass(item)">
                          {{ getCopyPlatformLabel(item) }}
                        </span>
                      </div>
                    </div>
                    <button class="publish-mini" type="button" @click="preparePublishFromCopy(item)">
                      <IconGlyph name="send" />
                      <span>发布</span>
                    </button>
                  </div>

                  <section class="copy-section">
                    <h3 class="copy-section-heading">标题:</h3>
                    <p class="copy-title-text">{{ item.title || `生成标题 ${index + 1}` }}</p>
                  </section>
                  <section class="copy-section">
                    <h3 class="copy-section-heading">文案:</h3>
                    <p class="copy-body-content">{{ getCopyBodyContent(item) }}</p>
                  </section>
                  <div v-if="getCopyDisplayTags(item).length" class="copy-accent-tags">
                    <span v-for="tag in getCopyDisplayTags(item)" :key="tag">{{ tag }}</span>
                  </div>
                </article>
              </div>
            </div>
          </section>
        </section>

        <section v-else-if="visiblePage === 'publish'" class="publish-page reference-publish-page" :class="`mode-${publishMode}`">
          <aside class="publish-subnav" aria-label="发布类型">
            <button :class="{ active: publishMode === 'article' }" type="button" @click="setPublishMode('article')">
              <IconGlyph name="document" />
              <span>发文章</span>
            </button>
            <button :class="{ active: publishMode === 'image' }" type="button" @click="setPublishMode('image')">
              <IconGlyph name="image" />
              <span>发图文</span>
            </button>
          </aside>

          <section v-if="publishMode === 'article'" class="publish-workbench publish-article-workbench">
            <div class="publish-editor-column article-publish-column">
              <article class="article-editor-card article-publish-editor">
                <div class="article-editor-head">
                  <button
                    class="ai-cover-button"
                    :disabled="publishLoading || publishImagePromptLoading"
                    type="button"
                    @click="generatePublishImage(0)"
                  >
                    AI自动配图
                  </button>
                </div>
                <div class="editor-toolbar" aria-label="编辑器工具栏">
                  <button type="button">正文</button>
                  <span></span>
                  <button class="tool-strong" type="button">B</button>
                  <button class="tool-italic" type="button">I</button>
                  <button class="tool-underline" type="button">U</button>
                  <button class="tool-strike" type="button">S</button>
                  <button type="button">&lt;/&gt;</button>
                  <button type="button">A</button>
                  <button type="button">⌁</button>
                  <span></span>
                  <button type="button">☰</button>
                  <button type="button">•</button>
                  <button type="button">1.</button>
                  <span></span>
                  <button type="button">⌁</button>
                  <button type="button">▧</button>
                  <button type="button">▦</button>
                  <button type="button">“</button>
                  <button type="button">{}</button>
                </div>
                <textarea
                  v-model="publishDraft.content"
                  :disabled="publishLoading"
                  placeholder="在此输入正文"
                ></textarea>
                <figure v-if="articleInlineImageUrl" class="article-inline-image">
                  <img :src="articleInlineImageUrl" alt="文章配图预览" />
                </figure>
              </article>
            </div>

            <aside class="publish-panel publish-article-panel">
              <article class="publish-settings reference-publish-settings article-side-settings">
                <input
                  ref="publishCoverFileInputRef"
                  class="visually-hidden-input"
                  type="file"
                  accept="image/*"
                  @change="handlePublishCoverFileChange"
                />
                <div class="publish-field-block">
                  <label>封面</label>
                  <button class="cover-upload-box" type="button" @click="choosePublishCover">
                    <img v-if="publishCoverPreviewUrl" :src="publishCoverPreviewUrl" alt="封面预览" />
                    <span v-else>
                      <IconGlyph name="upload" />
                      <strong>上传封面</strong>
                    </span>
                  </button>
                  <button class="cover-reference-link" type="button" @click="openCoverGuideDialog">
                    封面图参考
                    <IconGlyph name="help" />
                  </button>
                </div>

                <label class="input-field publish-field-block">
                  <span>标题</span>
                  <input
                    v-model="publishDraft.title"
                    :disabled="publishLoading"
                    type="text"
                    placeholder="请输入标题"
                  />
                </label>

                <label class="input-field publish-field-block">
                  <span>摘要</span>
                  <textarea
                    v-model="publishDraft.summary"
                    :disabled="publishLoading"
                    placeholder="请输入摘要"
                    rows="3"
                  ></textarea>
                </label>

                <label class="input-field publish-field-block">
                  <span>作者</span>
                  <input
                    v-model="publishDraft.author"
                    :disabled="publishLoading"
                    type="text"
                    placeholder="请输入作者"
                  />
                </label>

                <div class="input-field tag-field publish-field-block">
                  <span>标签</span>
                  <div class="tag-row">
                    <span v-for="tag in publishDraft.tags" :key="tag" class="tag-pill">
                      <span class="tag-text">{{ tag }}</span>
                      <button
                        class="tag-remove-button"
                        type="button"
                        :aria-label="`删除标签 ${tag}`"
                        @click.stop="removePublishTag(tag)"
                      >
                        ×
                      </button>
                    </span>
                  </div>
                  <input
                    v-model="tagInput"
                    :disabled="publishLoading"
                    type="text"
                    placeholder="添加新标签，按回车确认..."
                    @keydown.enter="handlePublishTagEnter"
                  />
                </div>

                <fieldset class="publish-platform-list">
                  <legend>发布平台</legend>
                  <label
                    v-for="(account, index) in publishAccountsForDisplay"
                    :key="account.id"
                    :class="{
                      checked: publishDraft.platforms.includes(account.id),
                      disabled: !isPublishableXhsAccount(account),
                      failed: !isPublishableXhsAccount(account)
                    }"
                  >
                    <span class="publish-platform-logo platform-wechat">
                      <IconGlyph name="message" />
                    </span>
                    <span>
                      <strong>{{ getPublishAccountName(account, index) }}</strong>
                      <em :class="{ failed: !isPublishableXhsAccount(account) }">
                        {{ getPublishAccountStatusText(account) }}
                      </em>
                    </span>
                    <input
                      v-model="publishDraft.platforms"
                      :disabled="publishLoading || !isPublishableXhsAccount(account)"
                      :value="account.id"
                      type="checkbox"
                    />
                  </label>
                  <p v-if="!publishAccountsForDisplay.length" class="publish-platform-empty">
                    暂无可发布账号
                  </p>
                </fieldset>
              </article>

              <p v-if="publishError" class="error-text publish-error">{{ publishError }}</p>
              <p v-if="publishSuccess" class="success-text publish-error">{{ publishSuccess }}</p>

              <div class="publish-action-card">
                <button class="publish-action" :disabled="publishLoading" type="button" @click="submitPublish">
                  <span>{{ publishLoading ? '发布中...' : '立即发布' }}</span>
                </button>
              </div>
            </aside>
          </section>

          <section v-else class="publish-workbench publish-image-workbench">
            <div class="publish-image-main">
              <article class="image-edit-card">
                <header>
                  <h2>图片编辑</h2>
                  <button
                    class="ai-cover-button"
                    :disabled="publishLoading || publishImagePromptLoading"
                    type="button"
                    @click="generatePublishImage(0)"
                  >
                    AI自动配图
                  </button>
                </header>
                <div class="image-edit-strip" aria-label="图文图片编辑">
                  <button
                    class="image-add-tile"
                    :disabled="publishLoading || publishImagePromptLoading"
                    type="button"
                    @click="generatePublishImage(0)"
                  >
                    <span>+</span>
                  </button>
                  <figure
                    v-for="slot in publishImageSlots"
                    :key="slot.id"
                    class="image-edit-thumb"
                    :class="`status-${slot.status}`"
                  >
                    <button
                      :disabled="publishLoading || publishImagePromptLoading || slot.status === 'generating'"
                      type="button"
                      @click="generatePublishImage(slot.index)"
                    >
                      <img v-if="slot.status === 'ready' && slot.imageUrl" :src="slot.imageUrl" :alt="slot.name" />
                      <span v-else-if="slot.status === 'generating'" class="image-thumb-skeleton" aria-hidden="true"></span>
                      <span v-else class="image-thumb-placeholder">
                        <IconGlyph name="image" />
                        <small>{{ slot.status === 'failed' ? '重试' : `图片${slot.index + 1}` }}</small>
                      </span>
                    </button>
                    <figcaption v-if="slot.status === 'failed'">{{ slot.error }}</figcaption>
                  </figure>
                </div>
              </article>

              <article class="image-caption-card">
                <h2>正文</h2>
                <textarea
                  v-model="publishDraft.content"
                  :disabled="publishLoading"
                  placeholder="输入正文描述，真诚有价值的分享予人温暖"
                ></textarea>
              </article>
            </div>

            <aside class="publish-panel publish-image-panel">
              <article class="publish-settings reference-publish-settings image-side-settings">
                <label class="input-field publish-field-block">
                  <span>标题</span>
                  <input
                    v-model="publishDraft.title"
                    :disabled="publishLoading"
                    type="text"
                    placeholder="请输入标题"
                  />
                </label>

                <div class="input-field tag-field publish-field-block">
                  <span>标签</span>
                  <div class="tag-row">
                    <span v-for="tag in publishDraft.tags" :key="tag" class="tag-pill">
                      <span class="tag-text">{{ tag.replace(/^#/, '') }}</span>
                      <button
                        class="tag-remove-button"
                        type="button"
                        :aria-label="`删除标签 ${tag}`"
                        @click.stop="removePublishTag(tag)"
                      >
                        ×
                      </button>
                    </span>
                  </div>
                  <input
                    v-model="tagInput"
                    :disabled="publishLoading"
                    type="text"
                    placeholder="添加新标签，按回车确认..."
                    @keydown.enter="handlePublishTagEnter"
                  />
                </div>

                <fieldset class="publish-platform-list">
                  <legend>发布平台</legend>
                  <label
                    v-for="(account, index) in publishAccountsForDisplay"
                    :key="account.id"
                    :class="{
                      checked: publishDraft.platforms.includes(account.id),
                      disabled: !isPublishableXhsAccount(account),
                      failed: !isPublishableXhsAccount(account)
                    }"
                  >
                    <span class="publish-platform-logo platform-xhs">
                      <span>小红书</span>
                    </span>
                    <span>
                      <strong>{{ getPublishAccountName(account, index) }}</strong>
                      <em :class="{ failed: !isPublishableXhsAccount(account) }">
                        {{ getPublishAccountStatusText(account) }}
                      </em>
                    </span>
                    <input
                      v-model="publishDraft.platforms"
                      :disabled="publishLoading || !isPublishableXhsAccount(account)"
                      :value="account.id"
                      type="checkbox"
                    />
                  </label>
                  <p v-if="!publishAccountsForDisplay.length" class="publish-platform-empty">
                    暂无可发布账号
                  </p>
                </fieldset>
              </article>

              <p v-if="publishError" class="error-text publish-error">{{ publishError }}</p>
              <p v-if="publishSuccess" class="success-text publish-error">{{ publishSuccess }}</p>

              <div class="publish-action-card">
                <button class="publish-action" :disabled="publishLoading" type="button" @click="submitPublish">
                  <span>{{ publishLoading ? '发布中...' : '立即发布' }}</span>
                </button>
              </div>
            </aside>
          </section>
        </section>

        <section v-else-if="visiblePage === 'accounts'" class="accounts-page">
          <article class="account-strip">
            <button
              v-for="account in accounts"
              :key="account.id"
              class="account-chip"
              :class="{ active: account.active }"
              type="button"
              @click="selectXhsAccount(account.id)"
            >
              <span class="account-avatar" :class="[account.avatarClass, { 'has-image': account.visibleAvatarUrl }]">
                <img
                  v-if="account.visibleAvatarUrl"
                  :src="account.visibleAvatarUrl"
                  :alt="`${account.displayName}头像`"
                  referrerpolicy="no-referrer"
                  @error="markAvatarAsBroken(account.id)"
                />
                <span v-else class="account-avatar-fallback">{{ account.initial }}</span>
                <img
                  v-if="account.status === 'saved'"
                  class="xhs-avatar-badge"
                  :src="xiaohongshuLogoUrl"
                  alt="小红书"
                />
              </span>
              <strong>{{ account.displayName }}</strong>
              <small>{{ formatAccountStatus(account) }}</small>
            </button>
          </article>

          <div class="account-actions">
            <button class="primary-lite" type="button" :disabled="xhsAccountLoading" @click="addXhsAccount">添加账号</button>
            <button class="primary-lite" type="button" :disabled="xhsAccountLoading || !activeXhsAccount" @click="saveActiveXhsSession(true)">同步账号</button>
            <button type="button">账号管理</button>
            <button type="button">账号分组</button>
            <button class="danger-lite" type="button" :disabled="xhsAccountLoading || !activeXhsAccount" @click="deleteActiveXhsAccount">
              <IconGlyph name="trash" />
              <span>删除账号</span>
            </button>
            <button type="button" :disabled="!activeXhsAccount" @click="openXhsLogin">一键重新登录</button>
          </div>

          <article class="login-browser-frame">
            <div class="login-window-title">
              <span>登录账号：{{ activeXhsAccount ? getAccountDisplayName(activeXhsAccount) : '小红书账号' }}</span>
              <div>
                <button type="button">□</button>
                <button type="button">×</button>
              </div>
            </div>
            <div class="browser-toolbar">
              <button type="button" title="后退" @click="goXhsBack"><IconGlyph name="arrowLeft" /></button>
              <button type="button" title="前进" @click="goXhsForward"><IconGlyph name="arrowRight" /></button>
              <button type="button" title="刷新" @click="refreshXhsWebview"><IconGlyph name="refresh" /></button>
              <button type="button" title="主页" @click="openXhsHome"><IconGlyph name="home" /></button>
              <span>{{ currentXhsUrl }}</span>
              <em>{{ activeXhsAccount?.partition ?? '未创建分区' }}</em>
              <em>{{ activeXhsAccount ? `${activeXhsAccount.cookieCount} cookies` : '0 cookies' }}</em>
              <small>− 100 +</small>
            </div>
            <div class="xiaohongshu-webview-wrap">
              <webview
                v-if="activeXhsAccount"
                :key="activeXhsAccount.id"
                ref="xiaohongshuWebviewRef"
                class="xiaohongshu-webview"
                :src="activeXhsStartUrl"
                :partition="activeXhsAccount.partition"
                useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                allowpopups
                @dom-ready="handleXhsDomReady"
                @did-finish-load="handleXhsLoadState"
                @did-navigate="handleXhsLoadState"
                @did-navigate-in-page="handleXhsLoadState"
              ></webview>
              <div v-else class="xiaohongshu-webview-empty">暂无小红书账号，请先添加账号</div>
            </div>
          </article>
        </section>
      </main>

      <footer v-if="showSuiteFooter" class="suite-footer">
        <button v-if="footerHistoryVisible" class="footer-history" type="button" @click="openHistory()">
          <IconGlyph name="history" />
          <span>{{ footerHistoryLabel }}</span>
        </button>
        <button v-if="visiblePage === 'trends'" class="download-report" type="button">
          <IconGlyph name="download" />
          <span>下载报告</span>
        </button>
      </footer>
    </section>

    <div v-if="historyDrawerOpen" class="drawer-scrim" @click.self="closeHistory">
      <aside class="history-drawer" aria-label="历史记录">
        <header>
          <h2>{{ historyDrawerTitle }}</h2>
          <button type="button" aria-label="关闭历史记录" @click="closeHistory">×</button>
        </header>
        <div v-if="!historyRecords.length" class="history-empty-state">
          <IconGlyph name="history" />
          <strong>暂无历史记录</strong>
          <span>{{ historyEmptyText }}</span>
        </div>
        <button
          v-for="item in historyRecords"
          :key="item.id"
          class="history-record"
          :class="{ active: item.id === selectedHistoryEntryId }"
          type="button"
          :aria-pressed="item.id === selectedHistoryEntryId"
          @click="selectHistoryRecord(item.id)"
        >
          <strong>{{ item.title }}</strong>
          <span>{{ item.time }}</span>
        </button>
      </aside>
    </div>

    <div v-if="helpDialogOpen" class="modal-scrim" @click.self="closeHelpDialog">
      <section class="qr-dialog" role="dialog" aria-modal="true" aria-label="帮助">
        <button class="modal-close" type="button" aria-label="关闭帮助" @click="closeHelpDialog">×</button>
        <div class="qr-dialog-body">
          <figure class="qr-item">
            <span class="qr-art qr-art-one" aria-hidden="true">
              <i>MDT</i>
            </span>
            <figcaption>专属客服</figcaption>
          </figure>
          <figure class="qr-item">
            <span class="qr-art qr-art-two" aria-hidden="true">
              <i>MDT</i>
            </span>
            <figcaption>关注我们</figcaption>
          </figure>
        </div>
      </section>
    </div>

    <div v-if="coverGuideDialogOpen" class="modal-scrim" @click.self="closeCoverGuideDialog">
      <section class="cover-guide-dialog" role="dialog" aria-modal="true" aria-label="封面图参考">
        <header>
          <h2>封面图参考</h2>
          <button class="modal-close" type="button" aria-label="关闭封面图参考" @click="closeCoverGuideDialog">×</button>
        </header>
        <div class="cover-ratio-visual" aria-hidden="true">
          <span class="cover-ratio-left"></span>
          <span class="cover-ratio-right"></span>
        </div>
        <strong>3.35:1</strong>
        <p>上传的图片会自动裁剪成规定比例，横版封面会从左边自动裁剪使用，方版封面会从右边自动裁剪使用</p>
      </section>
    </div>

    <SettingsDialog v-model:visible="settingsVisible" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch, type PropType } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SettingsDialog from '@components/SettingsDialog.vue'
import xiaohongshuLogoUrl from '../../../../assetes/xiaohongshu.png'
import brandLogoUrl from '../../../../logo/名称+小字.svg'
import {
  createImageGenerationTask,
  generateCopywriting,
  generatePublishImagePrompts,
  generateSeoKeywords,
  getImageGenerationTask,
  type CopywritingItem,
  type ImageGenerationStatusResponse,
  type PublishImagePromptItem,
  type SeoKeywordItem
} from '@api/generation'

type PageKey = 'trends' | 'seo' | 'copywriting' | 'publish' | 'accounts' | 'history'
type PrimaryNavPage = 'trends' | 'seo' | 'copywriting' | 'publish'
type IconName =
  | 'account'
  | 'alert'
  | 'arrowLeft'
  | 'arrowRight'
  | 'bell'
  | 'bulb'
  | 'chart'
  | 'check'
  | 'copy'
  | 'document'
  | 'download'
  | 'edit'
  | 'fire'
  | 'groups'
  | 'hash'
  | 'help'
  | 'history'
  | 'home'
  | 'image'
  | 'key'
  | 'link'
  | 'message'
  | 'refresh'
  | 'rocket'
  | 'search'
  | 'send'
  | 'settings'
  | 'shapes'
  | 'spark'
  | 'trend'
  | 'trash'
  | 'upload'
  | 'user'
  | 'video'

type SeoEntryRequest = {
  business: string
  features: string
  keywordCount: number
}

type CopyEntryRequest = {
  keyword: string
  keywordOccurrences: number
  articleCount: number
  platforms: string[]
}

type SeoGenerationEntry = {
  id: string
  type: 'seo'
  title: string
  createdAt: number
  request: SeoEntryRequest
  response: {
    items: SeoKeywordItem[]
    model: string
  }
}

type CopyGenerationEntry = {
  id: string
  type: 'copy'
  title: string
  createdAt: number
  request: CopyEntryRequest
  response: {
    items: CopywritingItem[]
    model: string
  }
}

type GenerationEntry = SeoGenerationEntry | CopyGenerationEntry
type HistoryType = GenerationEntry['type']
type PublishMode = 'article' | 'image'

type ChatSession = {
  id: string
  title: string
  createdAt: number
  updatedAt: number
  entries: GenerationEntry[]
}

type HistoryRecord = {
  id: string
  type: HistoryType
  title: string
  time: string
  createdAt: number
}

type SidebarNavItem = {
  id: string
  page?: PrimaryNavPage
  label: string
  icon: IconName
}

type XiaohongshuAccountStatus = 'pending' | 'saved'

type XiaohongshuAccount = {
  id: string
  platform: 'xiaohongshu'
  name: string
  nickname?: string
  avatarUrl?: string
  profileCapturedAt?: number
  partition: string
  status: XiaohongshuAccountStatus
  createdAt: number
  updatedAt: number
  lastLoginAt?: number
  lastSessionSaveAt?: number
  lastUrl?: string
  cookieCount: number
  localStorageCount: number
  sessionStorageCount: number
}

type XiaohongshuWebStorageSnapshot = {
  localStorage: Record<string, string>
  sessionStorage: Record<string, string>
  capturedAt: number
  url?: string
}

type XiaohongshuProfileSnapshot = {
  nickname?: string
  avatarUrl?: string
  capturedAt?: number
  isLoggedIn?: boolean
}

type XiaohongshuAccountView = XiaohongshuAccount & {
  active: boolean
  displayName: string
  initial: string
  avatarClass: string
  visibleAvatarUrl: string
}

type PublishImageSlotStatus = 'idle' | 'generating' | 'ready' | 'failed'

type PublishImageSlot = {
  id: string
  index: number
  status: PublishImageSlotStatus
  promptId: string
  name: string
  imageUrl: string
  promptDescription: string
  keywords: string[]
  sourceKey: string
  error: string
}

type XiaohongshuWebviewElement = HTMLElement & {
  canGoBack: () => boolean
  canGoForward: () => boolean
  executeJavaScript: <T = unknown>(code: string, userGesture?: boolean) => Promise<T>
  getURL: () => string
  goBack: () => void
  goForward: () => void
  loadURL: (url: string) => void
  reload: () => void
}

const SESSION_STORAGE_KEY = 'mdt-ai-agent.sessions.v1'
const XIAOHONGSHU_HOME_URL = 'https://creator.xiaohongshu.com'
const XIAOHONGSHU_LOGIN_URL = 'https://creator.xiaohongshu.com/login'
const XHS_AVATAR_CLASSES = ['avatar-lake', 'avatar-forest', 'avatar-sea']

const route = useRoute()
const router = useRouter()
const settingsVisible = ref(false)
const trendQuery = ref('')
const copyLength = ref('中等长度(200-300字)')
const sessions = ref<ChatSession[]>(loadSessions())
const activeSessionId = ref(ensureInitialSessionId(sessions.value))
const xiaohongshuWebviewRef = ref<XiaohongshuWebviewElement | null>(null)
const xhsAccounts = ref<XiaohongshuAccount[]>([])
const activeXhsAccountId = ref('')
const xhsAccountLoading = ref(false)
const xhsSessionMessage = ref('正在读取小红书账号环境...')
const currentXhsUrl = ref(XIAOHONGSHU_HOME_URL)
const xhsStartUrls = reactive<Record<string, string>>({})
const brokenAvatarAccountIds = ref<Set<string>>(new Set())
let xhsAutoSaveTimer: number | null = null
const restoredXhsStorageAccountIds = new Set<string>()
const activeHistoryType = ref<HistoryType>('seo')

const routeToPage = computed<PageKey>(() => {
  const page = route.meta.page
  return typeof page === 'string' ? (page as PageKey) : 'seo'
})
const historyVisiblePage = computed<PageKey>(() => (activeHistoryType.value === 'copy' ? 'copywriting' : 'seo'))
const visiblePage = computed<PageKey>(() => (routeToPage.value === 'history' ? historyVisiblePage.value : routeToPage.value))
const historyDrawerOpen = computed(() => routeToPage.value === 'history')
const activeNavPage = computed<PrimaryNavPage | 'accounts'>(() => {
  if (routeToPage.value === 'history') return historyVisiblePage.value as PrimaryNavPage
  if (visiblePage.value === 'accounts') return 'accounts'
  return visiblePage.value as PrimaryNavPage
})
const activeXhsAccount = computed(() => {
  return xhsAccounts.value.find((account) => account.id === activeXhsAccountId.value) ?? xhsAccounts.value[0] ?? null
})
const activeXhsStartUrl = computed(() => {
  const account = activeXhsAccount.value
  if (!account) return XIAOHONGSHU_HOME_URL
  return getXhsLaunchUrl(account)
})

const pageTitles: Record<PageKey, string> = {
  trends: '热点分析',
  seo: 'SEO关键词',
  copywriting: '宣传文案工具',
  publish: '发布中心',
  accounts: '账号管理',
  history: 'SEO关键词'
}
const headerTitle = computed(() => pageTitles[visiblePage.value] ?? 'SEO关键词')
const pageSubtitles: Partial<Record<PageKey, string>> = {
  copywriting: '一键生成爆款社媒文案',
  publish: '支持多平台发布',
  accounts: '官方内嵌网页账号管理',
  trends: '洞察内容机会'
}
const headerSubtitle = computed(() => pageSubtitles[visiblePage.value] ?? '')
const showSuiteHeader = computed(() => !['seo', 'copywriting'].includes(visiblePage.value))

const routeByPage: Record<PageKey, string> = {
  trends: '/trends',
  seo: '/seo',
  copywriting: '/copywriting',
  publish: '/publish',
  accounts: '/accounts',
  history: '/history'
}

const primaryNav: SidebarNavItem[] = [
  { id: 'seo', page: 'seo', label: '关键词生成', icon: 'shapes' },
  { id: 'copywriting', page: 'copywriting', label: '文案生成', icon: 'document' },
  { id: 'video', label: '视频脚本生成', icon: 'video' },
  { id: 'publish', page: 'publish', label: '发布中心', icon: 'send' }
]

const iconPaths: Record<IconName, string[]> = {
  account: [
    'M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
    'M15.5 10a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z',
    'M3.5 19a5.5 5.5 0 0 1 9.7-3.5',
    'M12.5 15.5a5 5 0 0 1 5.5-1.2',
    'M18.5 17.3l1-.6 1 .6v1.2l-1 .6-1-.6v-1.2Z',
    'M19.5 14.5v1',
    'M19.5 20.3v1',
    'M16.9 16l.9.5',
    'M21.2 19l.9.5',
    'M16.9 19.5l.9-.5',
    'M21.2 16.5l.9-.5'
  ],
  alert: ['M12 9v4', 'M12 17h.01', 'M10.3 4.2 2 2.8a2 2 0 0 0-3.4 0l-8.3 14.2A2 2 0 0 0 4.3 22h15.4a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0Z'],
  arrowLeft: ['M19 12H5', 'M12 19l-7-7 7-7'],
  arrowRight: ['M5 12h14', 'M12 5l7 7-7 7'],
  bell: ['M18 9a6 6 0 0 0-12 0c0 7-2 8-2 8h16s-2-1-2-8Z', 'M10 20a2 2 0 0 0 4 0'],
  bulb: ['M9 18h6', 'M10 22h4', 'M8.6 14.8A6 6 0 1 1 15.4 14.8c-.9.7-1.4 1.4-1.4 2.2h-4c0-.8-.5-1.5-1.4-2.2Z'],
  chart: ['M4 19V9', 'M10 19V5', 'M16 19v-7', 'M22 19H2'],
  check: ['M20 6 9 17l-5-5'],
  copy: ['M8 8h10v12H8z', 'M6 16H4V4h10v2'],
  document: ['M7 3h7l4 4v14H7V3Z', 'M14 3v5h5', 'M10 13h6', 'M10 17h4'],
  download: ['M12 3v12', 'M7 10l5 5 5-5', 'M5 21h14'],
  edit: ['M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4Z', 'M13.5 6.5l4 4'],
  fire: ['M12 22c4 0 7-2.8 7-6.4 0-2.7-1.4-5.1-3.5-6.5.1 2-1.1 3.2-2.5 3.7.4-2.9-.8-5.6-3.5-7.8.3 3.4-2.4 4.9-4 7.2C3.8 14 5 22 12 22Z'],
  groups: ['M17 21a5 5 0 0 0-10 0', 'M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z', 'M22 21a4 4 0 0 0-3-3.9', 'M2 21a4 4 0 0 1 3-3.9'],
  hash: ['M5 9h14', 'M5 15h14', 'M10 4 8 20', 'M16 4l-2 16'],
  help: ['M9.2 9a3 3 0 1 1 4.1 2.8c-.9.4-1.3 1-1.3 2.2', 'M12 18h.01'],
  history: ['M3 12a9 9 0 1 0 3-6.7', 'M3 4v5h5', 'M12 7v5l3 2'],
  home: ['M3 11 12 4l9 7', 'M5 10v10h14V10', 'M9 20v-6h6v6'],
  image: ['M4 5h16v14H4z', 'M8 13l2-2 3 3 2-2 3 4', 'M8 9h.01'],
  key: ['M15 7a4 4 0 1 0 2.8 6.8L22 18v3h-3v-2h-2v-2h-2l-1.8-1.8'],
  link: ['M10 13a5 5 0 0 0 7.1 0l2-2a5 5 0 0 0-7.1-7.1l-1.2 1.2', 'M14 11a5 5 0 0 0-7.1 0l-2 2A5 5 0 0 0 12 20.1l1.2-1.2'],
  message: ['M5 5h14v10H8l-3 3V5Z', 'M8 9h8', 'M8 12h5'],
  refresh: ['M20 12a8 8 0 0 1-13.7 5.7', 'M4 12A8 8 0 0 1 17.7 6.3', 'M17 3v4h4', 'M7 21v-4H3'],
  rocket: ['M5 16c-1 1-1.5 2.5-1.5 4.5C5.5 20.5 7 20 8 19', 'M15 9l-6 6', 'M9 15l-1 4 4-1 7.5-7.5A8 8 0 0 0 21 3a8 8 0 0 0-7.5 1.5L6 12l3 3Z'],
  search: ['M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z', 'M21 21l-4.3-4.3'],
  send: ['M22 2 11 13', 'M22 2l-7 20-4-9-9-4 20-7Z'],
  settings: [
    'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
    'M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z'
  ],
  shapes: ['M12 4l4.8 7H7.2L12 4Z', 'M5.5 13.5h5v5h-5z', 'M13.5 13.5h5v5h-5z'],
  spark: ['M12 3l1.7 4.4L18 9l-4.3 1.6L12 15l-1.7-4.4L6 9l4.3-1.6L12 3Z', 'M5 14l.8 2.2L8 17l-2.2.8L5 20l-.8-2.2L2 17l2.2-.8L5 14Z'],
  trend: ['M4 17l5-5 4 4 7-8', 'M14 8h6v6'],
  trash: ['M3 6h18', 'M8 6V4h8v2', 'M6 6l1 15h10l1-15', 'M10 11v6', 'M14 11v6'],
  upload: ['M12 16V4', 'M7 9l5-5 5 5', 'M5 20h14'],
  user: ['M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z', 'M4.5 20a7.5 7.5 0 0 1 15 0'],
  video: ['M4 7h10a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4V7Z', 'M16 10l4-2.5v9L16 14v-4Z']
}

const IconGlyph = defineComponent({
  name: 'IconGlyph',
  props: {
    name: {
      type: String as PropType<IconName>,
      required: true
    }
  },
  setup(props, { attrs }) {
    return () =>
      h(
        'svg',
        {
          ...attrs,
          viewBox: '0 0 24 24',
          fill: 'none',
          xmlns: 'http://www.w3.org/2000/svg',
          'aria-hidden': 'true'
        },
        iconPaths[props.name].map((path, index) =>
          h('path', {
            key: `${props.name}-${index}`,
            d: path,
            stroke: 'currentColor',
            'stroke-width': '1.85',
            'stroke-linecap': 'round',
            'stroke-linejoin': 'round'
          })
        )
      )
  }
})

const trendKeywords = [
  { text: 'AIGC', selected: true },
  { text: '机器学习', selected: false },
  { text: '自动化营销', selected: false },
  { text: '大语言模型', selected: false }
]
const hotContent = [
  { title: '2024年AI智能体发展趋势预测', views: '10w+ 阅读' },
  { title: '如何利用AI提升工作效率？', views: '8.5w 阅读' }
]
const competitors = [
  { short: 'A', name: '品牌 A', value: 45, color: '#0058be' },
  { short: 'B', name: '品牌 B', value: 30, color: '#526069' }
]
const audienceTags = ['25-34岁', '科技爱好者', '营销从业者', '高消费力']
const marketingAdvice = [
  '结合 "AIGC" 和 "工作效率" 创作干货类文章，预计能获得较高转化。',
  '针对 25-34 岁核心受众，建议在周三晚上 8 点推送视频内容。',
  '品牌A近期声量上升，建议监控其 "自动化营销" 相关活动。'
]

const seoForm = reactive({
  business: '',
  features: '',
  keywordCount: 10
})
const seoLoading = ref(false)
const seoError = ref('')
const seoResults = ref<SeoKeywordItem[]>([])
const seoModel = ref('')
const selectedSeoEntryId = ref('')
const displayedSeoResults = computed(() => seoResults.value)

const socialPlatforms = ['小红书', '公众号']
const copyForm = reactive({
  keyword: '',
  keywordOccurrences: 3,
  articleCount: 3,
  platform: '小红书'
})
const copyLoading = ref(false)
const copyError = ref('')
const copyResults = ref<CopywritingItem[]>([])
const copyModel = ref('')
const selectedCopyEntryId = ref('')
const displayedCopyResults = computed(() => copyResults.value)
const tagInput = ref('')
const PUBLISH_IMAGE_SLOT_COUNT = 3
const MIN_PUBLISH_IMAGE_COUNT = 1
const IMAGE_GENERATION_POLL_INTERVAL_MS = 2500
const IMAGE_GENERATION_TIMEOUT_MS = 10 * 60 * 1000
const PUBLISH_TAG_LIMIT = 7

const publishDraft = reactive({
  title: '',
  tags: ['#AI营销', '#数据分析', '#增长黑客'],
  content: '',
  summary: '',
  author: '',
  schedule: 'now',
  platforms: [] as string[]
})
const publishLoading = ref(false)
const publishError = ref('')
const publishSuccess = ref('')
const publishMode = ref<PublishMode>('article')
const publishImageSlots = ref<PublishImageSlot[]>(createPublishImageSlots())
const publishImagePrompts = ref<PublishImagePromptItem[]>([])
const publishImagePromptSourceKey = ref('')
const publishImagePromptLoading = ref(false)
const publishCoverFileInputRef = ref<HTMLInputElement | null>(null)
const publishCoverPreviewUrl = ref('')
const helpDialogOpen = ref(false)
const coverGuideDialogOpen = ref(false)
const coverUploadAfterGuide = ref(false)
const generatedPublishImages = computed(() =>
  publishImageSlots.value.filter(
    (slot) => slot.status === 'ready' && slot.imageUrl && slot.sourceKey === getPublishImageSourceKey()
  )
)
const articleInlineImageUrl = computed(() => generatedPublishImages.value[0]?.imageUrl || '')

const accounts = computed<XiaohongshuAccountView[]>(() =>
  xhsAccounts.value.map((account, index) => ({
    ...account,
    active: account.id === activeXhsAccount.value?.id,
    displayName: getAccountDisplayName(account),
    initial: getAccountInitial(account, index),
    avatarClass: XHS_AVATAR_CLASSES[index % XHS_AVATAR_CLASSES.length],
    visibleAvatarUrl: brokenAvatarAccountIds.value.has(account.id) ? '' : account.avatarUrl || ''
  }))
)
const publishAccountsForDisplay = computed(() => accounts.value)
const loggedInPublishAccounts = computed(() => accounts.value.filter(isPublishableXhsAccount))

const historyRecords = computed<HistoryRecord[]>(() =>
  sessions.value
    .flatMap((session) =>
      session.entries
        .filter((entry) => entry.type === activeHistoryType.value)
        .map((entry) => ({
          id: entry.id,
          type: entry.type,
          title: entry.title,
          time: formatDateTime(entry.createdAt),
          createdAt: entry.createdAt
        }))
    )
    .sort((a, b) => b.createdAt - a.createdAt)
)
const selectedHistoryEntryId = computed(() =>
  activeHistoryType.value === 'copy' ? selectedCopyEntryId.value : selectedSeoEntryId.value
)
const footerHistoryVisible = computed(() => false)
const footerHistoryLabel = computed(() => getHistoryButtonLabel(getHistoryTypeForPage(visiblePage.value)))
const showSuiteFooter = computed(() => footerHistoryVisible.value || visiblePage.value === 'trends')
const historyDrawerTitle = computed(() => getHistoryDrawerTitle(activeHistoryType.value))
const historyEmptyText = computed(() =>
  activeHistoryType.value === 'copy' ? '生成宣传文案后会显示在这里' : '生成 SEO 关键词后会显示在这里'
)

function goToPage(page: PageKey | PrimaryNavPage) {
  router.push(routeByPage[page as PageKey])
}

function openSettings() {
  settingsVisible.value = true
}

function openHelpDialog() {
  helpDialogOpen.value = true
}

function closeHelpDialog() {
  helpDialogOpen.value = false
}

function openCoverGuideDialog() {
  coverGuideDialogOpen.value = true
}

function closeCoverGuideDialog() {
  coverGuideDialogOpen.value = false
  if (!coverUploadAfterGuide.value) return

  coverUploadAfterGuide.value = false
  void nextTick(() => {
    publishCoverFileInputRef.value?.click()
  })
}

function setPublishMode(mode: PublishMode) {
  publishMode.value = mode
  publishError.value = ''
  publishSuccess.value = ''
}

function choosePublishCover() {
  coverUploadAfterGuide.value = true
  openCoverGuideDialog()
}

function handlePublishCoverFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  if (publishCoverPreviewUrl.value) {
    URL.revokeObjectURL(publishCoverPreviewUrl.value)
  }
  publishCoverPreviewUrl.value = URL.createObjectURL(file)
  input.value = ''
}

function openHistory(type: HistoryType = getHistoryTypeForPage(visiblePage.value)) {
  activeHistoryType.value = type
  router.push(routeByPage.history)
}

function closeHistory() {
  router.push(activeHistoryType.value === 'copy' ? routeByPage.copywriting : routeByPage.seo)
}

async function selectHistoryRecord(entryId: string) {
  if (activeHistoryType.value === 'copy') {
    const matched = findCopyHistoryEntry(entryId)
    if (!matched) return

    activeSessionId.value = matched.session.id
    hydrateCopyEntry(matched.entry)
    await router.push(routeByPage.copywriting)
    await nextTick()
    scrollSuiteContentToTop()
    return
  }

  const matched = findSeoHistoryEntry(entryId)
  if (!matched) return

  activeSessionId.value = matched.session.id
  hydrateSeoEntry(matched.entry)
  await router.push(routeByPage.seo)
  await nextTick()
  scrollSuiteContentToTop()
}

function findSeoHistoryEntry(entryId: string) {
  for (const session of sessions.value) {
    const entry = session.entries.find((item): item is SeoGenerationEntry => item.type === 'seo' && item.id === entryId)
    if (entry) return { session, entry }
  }
  return null
}

function findCopyHistoryEntry(entryId: string) {
  for (const session of sessions.value) {
    const entry = session.entries.find((item): item is CopyGenerationEntry => item.type === 'copy' && item.id === entryId)
    if (entry) return { session, entry }
  }
  return null
}

function hydrateSeoEntry(entry: SeoGenerationEntry) {
  seoForm.business = entry.request?.business || ''
  seoForm.features = entry.request?.features || ''
  seoForm.keywordCount = Number(entry.request?.keywordCount) || 10
  seoResults.value = Array.isArray(entry.response?.items) ? entry.response.items : []
  seoModel.value = entry.response?.model || ''
  seoError.value = ''
  seoLoading.value = false
  selectedSeoEntryId.value = entry.id
}

function hydrateCopyEntry(entry: CopyGenerationEntry) {
  const keywordOccurrences = Number(entry.request?.keywordOccurrences)
  const articleCount = Number(entry.request?.articleCount)
  const restoredPlatform = normalizeCopyPlatform(entry.request?.platforms?.[0] || '')

  copyForm.keyword = entry.request?.keyword || ''
  copyForm.keywordOccurrences = Number.isFinite(keywordOccurrences) ? keywordOccurrences : 3
  copyForm.articleCount = Number.isFinite(articleCount) && articleCount > 0 ? articleCount : 3
  copyForm.platform = restoredPlatform || '小红书'
  copyResults.value = Array.isArray(entry.response?.items) ? entry.response.items : []
  copyModel.value = entry.response?.model || ''
  copyError.value = ''
  copyLoading.value = false
  selectedCopyEntryId.value = entry.id
}

function normalizeCopyPlatform(platform: string) {
  if (/公众号|微信/u.test(platform)) return '公众号'
  if (/小红书|xhs|red/i.test(platform)) return '小红书'
  return socialPlatforms.includes(platform) ? platform : ''
}

function formatCopyIndex(index: number) {
  return String(index + 1).padStart(2, '0')
}

function getCopyPlatformLabel(item: CopywritingItem) {
  return normalizeCopyPlatform(item.platform || copyForm.platform) || '小红书'
}

function getCopyPlatformClass(item: CopywritingItem) {
  return getCopyPlatformLabel(item) === '公众号' ? 'platform-wechat' : 'platform-xhs'
}

function getCopyBodyContent(item: CopywritingItem) {
  return stripPublishTagsFromCopyContent(item.content) || item.content
}

function getCopyDisplayTags(item: CopywritingItem) {
  const tags: string[] = []

  for (const tag of extractCopyHashTags(`${item.title}\n${item.content}`)) {
    pushCopyDisplayTag(tags, tag)
  }

  for (const keyword of splitCopyKeywords(copyForm.keyword)) {
    pushCopyDisplayTag(tags, keyword)
  }

  pushCopyDisplayTag(tags, item.angle)

  return tags.slice(0, 6)
}

function pushCopyDisplayTag(tags: string[], value: string) {
  const normalized = normalizePublishTag(cleanKeywordCandidate(value))
  if (!normalized || tags.includes(normalized)) return
  tags.push(normalized)
}

function getHistoryTypeForPage(page: PageKey): HistoryType {
  return page === 'copywriting' ? 'copy' : 'seo'
}

function getHistoryButtonLabel(type: HistoryType) {
  return type === 'copy' ? '文案历史记录' : 'SEO关键词历史'
}

function getHistoryDrawerTitle(type: HistoryType) {
  return type === 'copy' ? '文案历史记录' : 'SEO关键词历史'
}

async function preparePublishFromCopy(item: CopywritingItem) {
  const title = getCopyPublishTitle(item)
  const content = stripPublishTagsFromCopyContent(item.content)
  const tags = derivePublishTagsFromCopy(item)

  publishDraft.title = title
  publishDraft.content = content
  publishDraft.summary = truncatePlainText(content.replace(/\s+/g, ' '), 80)
  publishDraft.tags.splice(0, publishDraft.tags.length, ...tags)
  publishDraft.schedule = 'now'
  tagInput.value = ''
  publishError.value = ''
  publishSuccess.value = ''
  publishImagePrompts.value = []
  publishImagePromptSourceKey.value = ''
  publishImageSlots.value = createPublishImageSlots()

  await router.push(routeByPage.publish)
  await nextTick()
  scrollSuiteContentToTop()
}

function getCopyPublishTitle(item: CopywritingItem) {
  const title = item.title.trim()
  if (title && !/^生成\d+$/.test(title)) return title

  const firstCandidate = collectPublishCopyCandidates(item.content)[0]
  return firstCandidate ? truncatePlainText(firstCandidate, 32) : title || '小红书图文'
}

function stripPublishTagsFromCopyContent(content: string) {
  const normalized = normalizeCopyText(content)
  if (!normalized) return ''

  const cleaned = normalized
    .split('\n')
    .map(cleanCopyContentLine)
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()

  return cleaned || normalized
}

function cleanCopyContentLine(line: string) {
  const withoutTags = line
    .replace(createCopyHashTagPattern(), '')
    .replace(/[ \t]{2,}/g, ' ')
    .replace(/[，,、；;：:]+$/u, '')
    .trimEnd()

  return /^(标签|话题|hashtags?)[:：]?\s*$/i.test(withoutTags.trim()) ? '' : withoutTags
}

function derivePublishTagsFromCopy(item: CopywritingItem) {
  const tags: string[] = []

  for (const tag of extractCopyHashTags(`${item.title}\n${item.content}`)) {
    pushPublishTag(tags, tag)
  }

  for (const keyword of splitCopyKeywords(copyForm.keyword)) {
    pushPublishTag(tags, keyword)
  }

  pushPublishTag(tags, item.angle)

  return tags.slice(0, PUBLISH_TAG_LIMIT)
}

function extractCopyHashTags(value: string) {
  return [...value.matchAll(createCopyHashTagPattern())].map((match) => match[1] || '')
}

function createCopyHashTagPattern() {
  return /[#＃]([A-Za-z0-9_\u4e00-\u9fa5][A-Za-z0-9_\u4e00-\u9fa5-]{0,24})/g
}

function splitCopyKeywords(value: string) {
  return value
    .split(/[，,、；;|/\n\r]+/u)
    .map((keyword) => keyword.trim())
    .filter(Boolean)
}

function pushPublishTag(tags: string[], value: string) {
  const normalized = normalizePublishTag(cleanKeywordCandidate(value))
  if (!normalized || tags.includes(normalized)) return
  tags.push(normalized)
}

function scrollSuiteContentToTop() {
  document.querySelector('.suite-content')?.scrollTo({ top: 0 })
}

function normalizePublishTag(value: string) {
  const text = value.trim().replace(/^[#＃]+/, '').trim()
  return text ? `#${text}` : ''
}

function addPublishTag() {
  const tag = normalizePublishTag(tagInput.value)
  if (!tag) return

  if (!publishDraft.tags.includes(tag)) {
    publishDraft.tags.push(tag)
  }
  tagInput.value = ''
}

function removePublishTag(tag: string) {
  const index = publishDraft.tags.indexOf(tag)
  if (index >= 0) {
    publishDraft.tags.splice(index, 1)
  }
}

function handlePublishTagEnter(event: KeyboardEvent) {
  if (event.isComposing) return

  event.preventDefault()
  addPublishTag()
}

function createPublishImageSlots(): PublishImageSlot[] {
  return Array.from({ length: PUBLISH_IMAGE_SLOT_COUNT }, (_, index) => ({
    id: `publish-image-slot-${index}`,
    index,
    status: 'idle',
    promptId: '',
    name: `图片 ${index + 1}`,
    imageUrl: '',
    promptDescription: '',
    keywords: [],
    sourceKey: '',
    error: ''
  }))
}

function collectPublishCopyCandidates(content: string) {
  const normalized = normalizeCopyText(content)
  if (!normalized) return []

  const lines = normalized.split(/\n+/).map((line) => line.trim()).filter(Boolean)
  const structured = lines
    .map(cleanCopyCandidate)
    .filter(isMeaningfulCopyCandidate)

  const paragraphs = normalized
    .split(/\n{2,}/)
    .map(cleanCopyCandidate)
    .filter(isMeaningfulCopyCandidate)

  const sentences = normalized
    .split(/[。！？!?]/)
    .map(cleanCopyCandidate)
    .filter(isMeaningfulCopyCandidate)

  return [...structured, ...paragraphs, ...sentences]
}

function normalizeCopyText(value: string) {
  return value
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function cleanCopyCandidate(value: string) {
  return value
    .replace(/^[\s#＃]*(?:[-*•]|[0-9]+[.、)）]|[一二三四五六七八九十]+[.、)）]|[①-⑩])\s*/u, '')
    .replace(/^#{1,6}\s*/, '')
    .replace(/[*_`]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

function isMeaningfulCopyCandidate(value: string) {
  if (value.length < 6) return false
  if (/^(核心亮点|核心卖点|核心优势|亮点|卖点|优势|总结|结尾|正文|标题)[:：]?$/.test(value)) return false
  return true
}

function cleanKeywordCandidate(value: string) {
  const keyword = value
    .replace(/^[\s#＃]*(?:[-*•]|[0-9]+[.、)）]|[一二三四五六七八九十]+[.、)）]|[①-⑩])\s*/u, '')
    .replace(/[“”"'`《》【】()\[\]（）]/g, '')
    .replace(/\s+/g, ' ')
    .trim()

  if (!keyword || keyword.length < 2 || /^[0-9.]+$/.test(keyword)) return ''
  if (/^(标题|标签|正文摘要|核心亮点|核心卖点|总结)$/.test(keyword)) return ''
  return truncatePlainText(keyword, 18)
}

async function generatePublishImage(slotIndex: number) {
  if (publishLoading.value) return

  const slot = publishImageSlots.value[slotIndex]
  if (!slot || slot.status === 'generating') return

  publishError.value = ''
  publishSuccess.value = ''

  try {
    const imagePrompts = await ensurePublishImagePrompts()
    const imagePrompt = imagePrompts[slotIndex]
    if (!imagePrompt?.description) {
      throw new Error(`第 ${slotIndex + 1} 张配图缺少文生图描述词`)
    }

    const sourceKey = getPublishImageSourceKey()
    setPublishImageSlot(slotIndex, {
      status: 'generating',
      promptId: '',
      imageUrl: '',
      promptDescription: imagePrompt.description,
      keywords: imagePrompt.keywords,
      sourceKey,
      error: '',
      name: `图片 ${slotIndex + 1}`
    })

    const task = await createImageGenerationTask({
      prompt: imagePrompt.description,
      width: 1920,
      height: 1080,
      batch_size: 1
    })

    setPublishImageSlot(slotIndex, {
      promptId: task.prompt_id
    })

    const result = await waitForPublishImage(task.prompt_id)
    if (!result.image?.url) {
      throw new Error('图片生成完成但未返回预览地址')
    }
    if (sourceKey !== getPublishImageSourceKey()) {
      throw new Error('文案内容已变化，请重新生成配图')
    }

    setPublishImageSlot(slotIndex, {
      status: 'ready',
      promptId: result.prompt_id,
      imageUrl: result.image.url,
      name: result.image.filename || `图片 ${slotIndex + 1}`,
      promptDescription: imagePrompt.description,
      keywords: imagePrompt.keywords,
      sourceKey,
      error: ''
    })
  } catch (error) {
    setPublishImageSlot(slotIndex, {
      status: 'failed',
      error: getErrorMessage(error),
      imageUrl: ''
    })
  }
}

async function ensurePublishImagePrompts() {
  if (!publishDraft.title.trim()) throw new Error('请先填写标题，再生成配图描述词')
  if (!publishDraft.content.trim()) throw new Error('请先填写正文，再生成配图描述词')

  const sourceKey = getPublishImageSourceKey()
  if (publishImagePromptSourceKey.value === sourceKey && publishImagePrompts.value.length >= PUBLISH_IMAGE_SLOT_COUNT) {
    return publishImagePrompts.value
  }

  publishImagePromptLoading.value = true
  publishImageSlots.value = createPublishImageSlots()

  try {
    const response = await generatePublishImagePrompts({
      title: publishDraft.title.trim(),
      content: publishDraft.content.trim(),
      tags: [...publishDraft.tags]
    })
    if (response.items.length < PUBLISH_IMAGE_SLOT_COUNT) {
      throw new Error(`配图描述词数量不足：期望 ${PUBLISH_IMAGE_SLOT_COUNT} 条，实际 ${response.items.length} 条`)
    }

    const items = response.items.slice(0, PUBLISH_IMAGE_SLOT_COUNT)
    publishImagePrompts.value = items
    publishImagePromptSourceKey.value = sourceKey
    publishImageSlots.value = createPublishImageSlots().map((slot) => {
      const item = items[slot.index]
      return {
        ...slot,
        promptDescription: item.description,
        keywords: item.keywords,
        sourceKey
      }
    })
    return items
  } finally {
    publishImagePromptLoading.value = false
  }
}

async function waitForPublishImage(promptId: string): Promise<ImageGenerationStatusResponse> {
  const startedAt = Date.now()

  while (Date.now() - startedAt < IMAGE_GENERATION_TIMEOUT_MS) {
    await delay(IMAGE_GENERATION_POLL_INTERVAL_MS)
    const result = await getImageGenerationTask(promptId)

    if (result.status === 'success') return result
    if (result.status === 'failed') {
      throw new Error(result.message || '图片生成失败')
    }
  }

  throw new Error('图片生成超时，请稍后重试')
}

function setPublishImageSlot(slotIndex: number, patch: Partial<PublishImageSlot>) {
  publishImageSlots.value = publishImageSlots.value.map((slot) => (slot.index === slotIndex ? { ...slot, ...patch } : slot))
}

function getPublishImageSourceKey() {
  return JSON.stringify({
    title: publishDraft.title.trim(),
    content: publishDraft.content.trim(),
    tags: publishDraft.tags.map((tag) => tag.trim()).filter(Boolean)
  })
}

function delay(ms: number) {
  return new Promise((resolveDelay) => {
    window.setTimeout(resolveDelay, ms)
  })
}

function validatePublishDraft() {
  if (!publishDraft.title.trim()) return '请输入标题'
  if (!publishDraft.content.trim()) return '请输入正文'
  if (generatedPublishImages.value.length < MIN_PUBLISH_IMAGE_COUNT) return '请至少生成 1 张配图'
  if (!publishDraft.platforms.length) return '请选择发布账号'
  if (publishDraft.schedule !== 'now') return '当前 RPA 图文发布仅支持立即发布'
  return ''
}

async function submitPublish() {
  const validation = validatePublishDraft()
  if (validation) {
    publishError.value = validation
    publishSuccess.value = ''
    return
  }

  publishLoading.value = true
  publishError.value = ''
  publishSuccess.value = ''

  try {
    const results: Array<{ status: 'published' | 'failed'; message?: string }> = []
    const accountIds = publishDraft.platforms.map((accountId) => String(accountId))
    const tags = publishDraft.tags.map((tag) => String(tag))
    const imageUrls = generatedPublishImages.value.map((image) => String(image.imageUrl))
    const title = publishDraft.title.trim()
    const content = publishDraft.content.trim()

    for (const accountId of accountIds) {
      results.push(
        await window.api.xiaohongshuPublisher.publishImageText({
          accountId,
          title,
          content,
          tags: [...tags],
          imageUrls: [...imageUrls]
        })
      )
    }

    const allPublished = results.every((item) => item.status === 'published')
    const failedResults = results.filter((item) => item.status === 'failed')

    if (allPublished) {
      publishSuccess.value = '发布成功'
    } else if (failedResults.length) {
      publishError.value = failedResults.map((item) => item.message || '发布失败').join('; ')
    }
  } catch (error) {
    publishError.value = getErrorMessage(error)
  } finally {
    publishLoading.value = false
  }
}

async function loadXhsAccounts() {
  xhsAccountLoading.value = true
  try {
    const loadedAccounts = await window.api.xiaohongshuAccounts.list()
    xhsAccounts.value = loadedAccounts
    const activeAccount = loadedAccounts.find((account) => account.id === activeXhsAccountId.value) ?? loadedAccounts[0]
    activeXhsAccountId.value = activeAccount?.id ?? ''
    currentXhsUrl.value = activeAccount?.lastUrl || XIAOHONGSHU_HOME_URL
    xhsSessionMessage.value = activeAccount ? '' : '请先添加小红书账号'
  } catch (error) {
    xhsSessionMessage.value = getErrorMessage(error)
  } finally {
    xhsAccountLoading.value = false
  }
}

async function addXhsAccount() {
  xhsAccountLoading.value = true
  try {
    const account = await window.api.xiaohongshuAccounts.create()
    xhsAccounts.value = [...xhsAccounts.value, account]
    activeXhsAccountId.value = account.id
    xhsStartUrls[account.id] = XIAOHONGSHU_LOGIN_URL
    currentXhsUrl.value = XIAOHONGSHU_LOGIN_URL
    xhsSessionMessage.value = '已创建独立登录环境，请在下方完成小红书登录'
    await nextTick()
    openXhsLogin()
  } catch (error) {
    xhsSessionMessage.value = getErrorMessage(error)
  } finally {
    xhsAccountLoading.value = false
  }
}

async function deleteActiveXhsAccount() {
  const account = activeXhsAccount.value
  if (!account || xhsAccountLoading.value) return

  const accountName = getAccountDisplayName(account)
  const confirmed = window.confirm(`确定删除「${accountName}」吗？该账号的 Cookie、缓存和本地登录数据也会被清除。`)
  if (!confirmed) return

  if (xhsAutoSaveTimer) {
    window.clearTimeout(xhsAutoSaveTimer)
    xhsAutoSaveTimer = null
  }

  xhsAccountLoading.value = true
  try {
    const deletedIndex = xhsAccounts.value.findIndex((item) => item.id === account.id)
    const remainingAccounts = await window.api.xiaohongshuAccounts.delete(account.id)
    xhsAccounts.value = remainingAccounts

    delete xhsStartUrls[account.id]
    restoredXhsStorageAccountIds.delete(account.id)
    const nextBrokenIds = new Set(brokenAvatarAccountIds.value)
    nextBrokenIds.delete(account.id)
    brokenAvatarAccountIds.value = nextBrokenIds

    const nextAccount = remainingAccounts[deletedIndex] ?? remainingAccounts[deletedIndex - 1] ?? remainingAccounts[0]
    activeXhsAccountId.value = nextAccount?.id ?? ''
    currentXhsUrl.value = nextAccount ? getXhsLaunchUrl(nextAccount) : XIAOHONGSHU_HOME_URL
    xhsSessionMessage.value = nextAccount
      ? `已删除 ${accountName}，当前切换到 ${getAccountDisplayName(nextAccount)}`
      : `已删除 ${accountName}，请添加小红书账号`
  } catch (error) {
    xhsSessionMessage.value = getErrorMessage(error)
  } finally {
    xhsAccountLoading.value = false
  }
}

function selectXhsAccount(accountId: string) {
  const account = xhsAccounts.value.find((item) => item.id === accountId)
  if (!account) return

  activeXhsAccountId.value = account.id
  if (account.status === 'saved' && isXhsLoginUrl(xhsStartUrls[account.id])) {
    delete xhsStartUrls[account.id]
  }
  currentXhsUrl.value = getXhsLaunchUrl(account)
  xhsSessionMessage.value =
    account.status === 'saved'
      ? `已切换到 ${getAccountDisplayName(account)}`
      : `已切换到 ${getAccountDisplayName(account)}，请完成小红书登录`
}

function openXhsLogin() {
  navigateXhsWebview(XIAOHONGSHU_LOGIN_URL)
}

function openXhsHome() {
  navigateXhsWebview(XIAOHONGSHU_HOME_URL)
}

function goXhsBack() {
  const webview = getXhsWebview()
  if (webview?.canGoBack()) {
    webview.goBack()
  }
}

function goXhsForward() {
  const webview = getXhsWebview()
  if (webview?.canGoForward()) {
    webview.goForward()
  }
}

function refreshXhsWebview() {
  getXhsWebview()?.reload()
}

function navigateXhsWebview(url: string) {
  const account = activeXhsAccount.value
  if (account) {
    xhsStartUrls[account.id] = url
  }
  currentXhsUrl.value = url
  getXhsWebview()?.loadURL(url)
}

async function handleXhsDomReady() {
  syncCurrentXhsUrl()
  await restoreXhsWebStorage()
}

function handleXhsLoadState() {
  syncCurrentXhsUrl()
  if (looksLikeLoggedInXhsUrl(currentXhsUrl.value)) {
    scheduleAutoSaveXhsSession()
  }
}

function syncCurrentXhsUrl() {
  const url = getXhsWebview()?.getURL()
  if (url) {
    currentXhsUrl.value = url
  }
}

function scheduleAutoSaveXhsSession() {
  if (xhsAutoSaveTimer) {
    window.clearTimeout(xhsAutoSaveTimer)
  }

  xhsAutoSaveTimer = window.setTimeout(() => {
    void saveActiveXhsSession(false)
  }, 1200)
}

async function saveActiveXhsSession(manual = false) {
  const account = activeXhsAccount.value
  const webview = getXhsWebview()
  if (!account || !webview || xhsAccountLoading.value) return

  xhsAccountLoading.value = true
  try {
    syncCurrentXhsUrl()
    const [webStorage, title, profile] = await Promise.all([
      collectXhsWebStorage(webview),
      readXhsDocumentTitle(webview),
      collectXhsProfile(webview)
    ])
    const savedAccount = await window.api.xiaohongshuAccounts.saveSession({
      accountId: account.id,
      url: currentXhsUrl.value,
      title,
      profile,
      webStorage
    })
    updateXhsAccount(savedAccount)
    if (savedAccount.status === 'saved') {
      delete xhsStartUrls[savedAccount.id]
      currentXhsUrl.value = getXhsLaunchUrl(savedAccount)
    }
    if (manual) {
      xhsSessionMessage.value =
        savedAccount.status === 'saved'
          ? `已同步 ${getAccountDisplayName(savedAccount)} 的 Cookie/session`
          : '当前页面还没有可保存的登录态，请完成小红书登录'
    } else if (savedAccount.status !== 'saved') {
      xhsSessionMessage.value = '当前页面还没有可保存的登录态，请完成小红书登录'
    }
  } catch (error) {
    xhsSessionMessage.value = getErrorMessage(error)
  } finally {
    xhsAccountLoading.value = false
  }
}

async function restoreXhsWebStorage() {
  const account = activeXhsAccount.value
  const webview = getXhsWebview()
  if (!account || !webview || restoredXhsStorageAccountIds.has(account.id)) return

  try {
    const snapshot = await window.api.xiaohongshuAccounts.getWebStorage(account.id)
    if (!snapshot) return

    await webview.executeJavaScript(
      `(() => {
        const restore = (target, data) => {
          Object.entries(data || {}).forEach(([key, value]) => {
            if (typeof key === 'string' && typeof value === 'string') {
              target.setItem(key, value)
            }
          })
        }
        restore(window.localStorage, ${JSON.stringify(snapshot.localStorage)})
        restore(window.sessionStorage, ${JSON.stringify(snapshot.sessionStorage)})
      })()`
    )
    restoredXhsStorageAccountIds.add(account.id)
  } catch (error) {
    console.warn('恢复小红书 Web Storage 失败', error)
  }
}

async function collectXhsWebStorage(webview: XiaohongshuWebviewElement): Promise<XiaohongshuWebStorageSnapshot> {
  try {
    return await webview.executeJavaScript<XiaohongshuWebStorageSnapshot>(
      `(() => {
        const dump = (target) => {
          const result = {}
          for (let index = 0; index < target.length; index += 1) {
            const key = target.key(index)
            if (key) result[key] = target.getItem(key) || ''
          }
          return result
        }
        return {
          localStorage: dump(window.localStorage),
          sessionStorage: dump(window.sessionStorage),
          capturedAt: Date.now(),
          url: window.location.href
        }
      })()`
    )
  } catch {
    return {
      localStorage: {},
      sessionStorage: {},
      capturedAt: Date.now(),
      url: currentXhsUrl.value
    }
  }
}

async function collectXhsProfile(webview: XiaohongshuWebviewElement): Promise<XiaohongshuProfileSnapshot> {
  try {
    return await webview.executeJavaScript<XiaohongshuProfileSnapshot>(
      `(() => {
        const candidates = []
        const seen = new WeakSet()
        const nicknameKeyPattern = /nick.?name|nickname|user.?name|display.?name|^name$/i
        const avatarKeyPattern = /avatar|head.?image|head.?url|profile.?image|image.?url|icon|portrait/i

        const normalizeText = (value) => {
          if (typeof value !== 'string') return ''
          return value.replace(/\\s+/g, ' ').trim().slice(0, 32)
        }

        const normalizeUrl = (value) => {
          if (typeof value !== 'string') return ''
          const text = value.trim()
          if (!text || text.startsWith('data:') || text.startsWith('blob:')) return ''
          try {
            const url = new URL(text, window.location.href)
            return /^https?:$/.test(url.protocol) ? url.href : ''
          } catch {
            return ''
          }
        }

        const isUsefulNickname = (value) => {
          const text = normalizeText(value)
          if (!text || text.length > 32) return false
          return !/(登录|注册|首页|发布|消息|通知|设置|帮助|创作服务平台|账号管理|小红书号|关注|粉丝|获赞|扫码)/.test(text)
        }

        const pushCandidate = (candidate, source) => {
          const nickname = isUsefulNickname(candidate.nickname) ? normalizeText(candidate.nickname) : ''
          const avatarUrl = normalizeUrl(candidate.avatarUrl)
          if (nickname || avatarUrl) {
            candidates.push({ nickname, avatarUrl, source })
          }
        }

        const inspectObject = (value, depth = 0) => {
          if (!value || typeof value !== 'object' || depth > 5 || seen.has(value)) return
          seen.add(value)

          let nickname = ''
          let avatarUrl = ''
          Object.entries(value).forEach(([key, item]) => {
            if (typeof item !== 'string') return

            if (!nickname && nicknameKeyPattern.test(key) && isUsefulNickname(item)) {
              nickname = item
            }

            if (!avatarUrl && avatarKeyPattern.test(key)) {
              avatarUrl = normalizeUrl(item)
            }
          })

          pushCandidate({ nickname, avatarUrl }, 'storage')

          Object.values(value).forEach((item) => inspectObject(item, depth + 1))
        }

        const inspectStorage = (storage) => {
          for (let index = 0; index < storage.length; index += 1) {
            const key = storage.key(index)
            const raw = key ? storage.getItem(key) : ''
            if (!raw || !/^\\s*[{[]/.test(raw)) continue

            try {
              inspectObject(JSON.parse(raw))
            } catch {
              // Ignore unrelated storage entries.
            }
          }
        }

        inspectStorage(window.localStorage)
        inspectStorage(window.sessionStorage)

        const metaTitle = document.querySelector('meta[property="og:title"], meta[name="og:title"]')?.getAttribute('content')
        const metaImage = document.querySelector('meta[property="og:image"], meta[name="og:image"]')?.getAttribute('content')
        pushCandidate({ nickname: metaTitle, avatarUrl: isUsefulNickname(metaTitle) ? metaImage : '' }, 'meta')

        Array.from(document.querySelectorAll('img')).slice(0, 160).forEach((image) => {
          const avatarUrl = normalizeUrl(image.currentSrc || image.src || image.getAttribute('src') || '')
          if (!avatarUrl) return

          const imageHint = [
            image.alt,
            image.title,
            image.className,
            image.getAttribute('aria-label'),
            avatarUrl
          ]
            .filter(Boolean)
            .join(' ')

          if (!/(avatar|head|profile|user|portrait|face)/i.test(imageHint)) return

          const container = image.closest('[class*="user"], [class*="avatar"], [class*="profile"], [class*="account"], header, button, a, div')
          const textParts = normalizeText((container && container.textContent) || image.alt || image.title || '')
            .split(' ')
            .filter(isUsefulNickname)
          pushCandidate({ nickname: textParts[0] || image.alt || image.title || '', avatarUrl }, 'dom')
        })

        const score = (candidate) => {
          let value = 0
          if (candidate.nickname) value += 40
          if (candidate.avatarUrl) value += 50
          if (candidate.source === 'storage') value += 20
          if (candidate.source === 'meta') value += 10
          if (/(avatar|head|profile|xhscdn|xhslink|xiaohongshu|sns)/i.test(candidate.avatarUrl || '')) value += 10
          return value
        }

        const best = candidates.sort((left, right) => score(right) - score(left))[0] || {}
        const pageText = ((document.body && document.body.innerText) || '').replace(/\\s+/g, ' ').trim().slice(0, 4000)
        const isLoginRoute = /\\/login(?:\\/|$)/.test(window.location.pathname)
        const hasLoginPrompt = /(登录|注册|验证码登录|密码登录|扫码登录|手机号登录)/.test(pageText)
        const hasCreatorWorkspace = /(发布笔记|发布作品|笔记管理|数据看板|创作中心|创作者服务|账号数据|互动管理|评论管理|粉丝管理)/.test(pageText)
        const hasProfileCandidate = Boolean(best.nickname || best.avatarUrl)
        const isLoggedIn =
          !isLoginRoute && (hasProfileCandidate || hasCreatorWorkspace) && !(hasLoginPrompt && !hasCreatorWorkspace && !hasProfileCandidate)

        return {
          nickname: best.nickname || '',
          avatarUrl: best.avatarUrl || '',
          capturedAt: Date.now(),
          isLoggedIn
        }
      })()`
    )
  } catch {
    return {
      capturedAt: Date.now()
    }
  }
}

async function readXhsDocumentTitle(webview: XiaohongshuWebviewElement): Promise<string> {
  try {
    return await webview.executeJavaScript<string>('document.title || ""')
  } catch {
    return ''
  }
}

function getXhsWebview() {
  return xiaohongshuWebviewRef.value
}

function updateXhsAccount(account: XiaohongshuAccount) {
  if (account.avatarUrl) {
    const nextBrokenIds = new Set(brokenAvatarAccountIds.value)
    nextBrokenIds.delete(account.id)
    brokenAvatarAccountIds.value = nextBrokenIds
  }
  xhsAccounts.value = xhsAccounts.value.map((item) => (item.id === account.id ? account : item))
}

function markAvatarAsBroken(accountId: string) {
  brokenAvatarAccountIds.value = new Set(brokenAvatarAccountIds.value).add(accountId)
}

function looksLikeLoggedInXhsUrl(url: string) {
  try {
    const parsed = new URL(url)
    return parsed.hostname.endsWith('xiaohongshu.com') && !parsed.pathname.includes('/login')
  } catch {
    return false
  }
}

function getXhsLaunchUrl(account: XiaohongshuAccount) {
  const temporaryUrl = xhsStartUrls[account.id]
  if (temporaryUrl && (account.status !== 'saved' || !isXhsLoginUrl(temporaryUrl))) {
    return temporaryUrl
  }
  if (account.lastUrl && !isXhsLoginUrl(account.lastUrl)) {
    return account.lastUrl
  }
  return XIAOHONGSHU_HOME_URL
}

function isXhsLoginUrl(url?: string) {
  if (!url) return false
  try {
    const parsed = new URL(url)
    return parsed.hostname.endsWith('xiaohongshu.com') && parsed.pathname.includes('/login')
  } catch {
    return url.includes('/login')
  }
}

function isPublishableXhsAccount(account: XiaohongshuAccount) {
  return account.status === 'saved' && !isXhsLoginUrl(account.lastUrl)
}

function getPublishAccountName(account: XiaohongshuAccountView, index: number) {
  const platformName = publishMode.value === 'article' ? '公众号' : '小红书'
  const normalizedName = getAccountDisplayName(account)
    .replace(/^小红书账号\s*/u, '')
    .replace(/^(小红书|公众号)[（(]?/u, '')
    .replace(/[)）]$/u, '')
    .trim()
  const suffix = normalizedName
    ? /^\d+$/u.test(normalizedName)
      ? `用户${normalizedName}`
      : normalizedName
    : `用户${index + 1}`

  return `${platformName}（${suffix}）`
}

function getPublishAccountStatusText(account: XiaohongshuAccount) {
  return isPublishableXhsAccount(account) ? '已连接' : '连接失败'
}

function getAccountDisplayName(account: XiaohongshuAccount) {
  return account.nickname?.trim() || account.name
}

function getAccountInitial(account: XiaohongshuAccount, index: number) {
  const name = getAccountDisplayName(account).replace(/^小红书账号\s*/u, '').trim()
  return (name[0] || `${index + 1}`).slice(0, 1)
}

function formatAccountStatus(account: XiaohongshuAccount) {
  if (account.status !== 'saved') {
    return account.lastSessionSaveAt ? '未登录/需重新登录' : '未保存登录态'
  }
  return `已保存 · ${formatDateTime(account.lastSessionSaveAt || account.updatedAt)}`
}

function analyzeTrends() {
  if (!trendQuery.value.trim()) {
    trendQuery.value = 'AI 智能体'
  }
}

async function submitSeo() {
  const validation = validateSeoForm()
  if (validation) {
    seoError.value = validation
    return
  }

  seoLoading.value = true
  seoError.value = ''
  const requestPayload: SeoEntryRequest = {
    business: seoForm.business.trim(),
    features: seoForm.features.trim(),
    keywordCount: Number(seoForm.keywordCount)
  }

  try {
    const response = await generateSeoKeywords({
      business_description: requestPayload.business,
      product_features: requestPayload.features,
      keyword_count: requestPayload.keywordCount,
      search_engines: ['百度', '360搜索', '必应']
    })
    seoResults.value = response.items
    seoModel.value = response.model
    const entry: SeoGenerationEntry = {
      id: createId(),
      type: 'seo',
      title: truncateTitle(`SEO：${requestPayload.business}`),
      createdAt: Date.now(),
      request: requestPayload,
      response
    }
    appendSessionEntry(entry)
    selectedSeoEntryId.value = entry.id
  } catch (error) {
    seoError.value = getErrorMessage(error)
  } finally {
    seoLoading.value = false
  }
}

function resetSeoResults() {
  seoResults.value = []
  seoModel.value = ''
  selectedSeoEntryId.value = ''
}

async function prepareCopyFromKeyword(keyword: string) {
  copyForm.keyword = keyword
  copyForm.keywordOccurrences = Math.max(copyForm.keywordOccurrences, 1)
  selectedCopyEntryId.value = ''
  await router.push(routeByPage.copywriting)
  await nextTick()
}

async function submitCopy() {
  const validation = validateCopyForm()
  if (validation) {
    copyError.value = validation
    return
  }

  copyLoading.value = true
  copyError.value = ''
  const requestPayload: CopyEntryRequest = {
    keyword: copyForm.keyword.trim(),
    keywordOccurrences: Number(copyForm.keywordOccurrences),
    articleCount: Number(copyForm.articleCount),
    platforms: [copyForm.platform]
  }

  try {
    const response = await generateCopywriting({
      keyword: requestPayload.keyword,
      keyword_repeat_count: requestPayload.keywordOccurrences,
      article_count: requestPayload.articleCount,
      platform_styles: requestPayload.platforms
    })
    copyResults.value = response.items
    copyModel.value = response.model
    const entry: CopyGenerationEntry = {
      id: createId(),
      type: 'copy',
      title: truncateTitle(`文案：${requestPayload.keyword}`),
      createdAt: Date.now(),
      request: requestPayload,
      response
    }
    appendSessionEntry(entry)
    selectedCopyEntryId.value = entry.id
  } catch (error) {
    copyError.value = getErrorMessage(error)
  } finally {
    copyLoading.value = false
  }
}

function validateSeoForm() {
  if (!seoForm.business.trim()) return '请输入业务描述'
  if (!seoForm.features.trim()) return '请输入产品特点'
  if (!Number.isFinite(Number(seoForm.keywordCount)) || seoForm.keywordCount < 1 || seoForm.keywordCount > 100) {
    return '关键词数量需在 1-100 之间'
  }
  return ''
}

function validateCopyForm() {
  if (!copyForm.keyword.trim()) return '请输入关键词'
  if (!socialPlatforms.includes(copyForm.platform)) return '请选择小红书或公众号'
  if (!Number.isFinite(Number(copyForm.articleCount)) || copyForm.articleCount < 1) {
    return '生成篇数需大于 0'
  }
  return ''
}

function appendSessionEntry(entry: GenerationEntry) {
  const currentSession = sessions.value.find((session) => session.id === activeSessionId.value)
  const target = currentSession ?? createEmptySession()
  if (!currentSession) {
    sessions.value.unshift(target)
    activeSessionId.value = target.id
  }
  target.entries.push(entry)
  target.title = entry.title
  target.updatedAt = entry.createdAt
  saveSessions(sessions.value)
}

function ensureInitialSessionId(items: ChatSession[]) {
  if (items.length) {
    return [...items].sort((a, b) => b.updatedAt - a.updatedAt)[0].id
  }

  const session = createEmptySession()
  items.push(session)
  saveSessions(items)
  return session.id
}

function createEmptySession(): ChatSession {
  const now = Date.now()
  return {
    id: createId(),
    title: '新会话',
    createdAt: now,
    updatedAt: now,
    entries: []
  }
}

function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as ChatSession[]
    if (!Array.isArray(parsed)) return []
    return parsed.filter((session) => Boolean(session?.id && session.title && Array.isArray(session.entries)))
  } catch (error) {
    console.warn('读取会话记录失败', error)
    return []
  }
}

function saveSessions(items: ChatSession[]) {
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(items))
}

function createId() {
  if (crypto.randomUUID) return crypto.randomUUID()
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function truncateTitle(value: string) {
  return value.length > 18 ? `${value.slice(0, 18)}...` : value
}

function truncatePlainText(value: string, maxLength: number) {
  return value.length > maxLength ? `${value.slice(0, maxLength)}...` : value
}

function formatDateTime(timestamp: number) {
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) return error.message
  return '请求失败，请检查模型设置或稍后重试'
}

watch(
  () => getPublishImageSourceKey(),
  (sourceKey) => {
    const hasImagePromptState =
      Boolean(publishImagePromptSourceKey.value) ||
      publishImagePrompts.value.length > 0 ||
      publishImageSlots.value.some((slot) => slot.status !== 'idle' || Boolean(slot.promptDescription))

    if (!hasImagePromptState || publishImagePromptSourceKey.value === sourceKey) return

    publishImagePrompts.value = []
    publishImagePromptSourceKey.value = ''
    publishImageSlots.value = createPublishImageSlots()
  }
)

watch(
  loggedInPublishAccounts,
  (publishAccounts) => {
    const availableAccountIds = new Set(publishAccounts.map((account) => account.id))
    const selectedAccountIds = publishDraft.platforms.filter((accountId) => availableAccountIds.has(accountId))

    if (!selectedAccountIds.length && publishAccounts.length) {
      selectedAccountIds.push(publishAccounts[0].id)
    }

    publishDraft.platforms.splice(0, publishDraft.platforms.length, ...selectedAccountIds)
  },
  { immediate: true }
)

onMounted(() => {
  document.title = 'Market Sales'
  void loadXhsAccounts()
})

onBeforeUnmount(() => {
  if (xhsAutoSaveTimer) {
    window.clearTimeout(xhsAutoSaveTimer)
  }
  if (publishCoverPreviewUrl.value) {
    URL.revokeObjectURL(publishCoverPreviewUrl.value)
  }
})
</script>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  width: 100%;
  height: 100%;
  margin: 0;
}

:global(body) {
  overflow: hidden;
  background: #f8f9fa;
  color: #191c1d;
  font-family:
    Inter,
    'Microsoft YaHei',
    'PingFang SC',
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
}

:global(*) {
  box-sizing: border-box;
}

:global(button),
:global(input),
:global(textarea),
:global(select) {
  font: inherit;
}

.suite-shell {
  --primary: #0058be;
  --primary-strong: #004d99;
  --primary-soft: #d6e3ff;
  --surface: #ffffff;
  --surface-low: #f3f4f5;
  --surface-container: #edeeef;
  --surface-high: #e7e8e9;
  --surface-highest: #e1e3e4;
  --text: #191c1d;
  --text-muted: #424752;
  --outline: #c2c6d4;
  --outline-dark: #727783;
  --error: #ba1a1a;
  --success: #005c16;
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #f8f9fa;
  color: var(--text);
}

.suite-shell svg {
  width: 22px;
  height: 22px;
  flex: 0 0 22px;
}

.suite-sidebar {
  display: flex;
  width: 276px;
  height: 100vh;
  flex: 0 0 276px;
  flex-direction: column;
  border-right: 1px solid var(--outline);
  background: #ffffff;
  padding: 28px 14px 24px;
}

.suite-brand {
  display: flex;
  height: 76px;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  margin-bottom: 24px;
}

.suite-brand img {
  display: block;
  width: 100%;
  max-width: 206px;
  max-height: 64px;
  object-fit: contain;
  object-position: center;
}

.suite-nav {
  display: grid;
  gap: 10px;
}

.nav-secondary {
  margin-top: 26px;
  border-top: 1px solid var(--outline);
  padding-top: 26px;
}

.nav-item,
.help-center,
.icon-button,
.ghost-button,
.primary-action,
.link-action,
.publish-mini,
.account-actions button,
.primary-lite,
.publish-action,
.tag-remove-button,
.footer-history,
.download-report,
.history-record {
  border: 0;
  cursor: pointer;
}

.nav-item {
  display: flex;
  min-height: 50px;
  align-items: center;
  gap: 16px;
  border-radius: 8px;
  background: transparent;
  color: #30363d;
  padding: 0 20px;
  text-align: left;
  transition:
    background-color 0.16s ease,
    color 0.16s ease;
}

.nav-item span {
  font-size: 18px;
  line-height: 24px;
}

.nav-item:hover {
  background: var(--surface-low);
}

.nav-item.active {
  background: #2f7dd2;
  color: #ffffff;
  font-weight: 700;
}

.help-center {
  display: flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: auto;
  border-radius: 8px;
  background: #edf4fb;
  color: var(--primary);
  font-weight: 700;
}

.suite-main {
  display: flex;
  min-width: 0;
  height: 100vh;
  flex: 1;
  flex-direction: column;
}

.suite-header {
  display: flex;
  height: 70px;
  flex: 0 0 70px;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--outline);
  background: #ffffff;
  padding: 0 30px;
}

.suite-header h1 {
  margin: 0;
  color: #05070a;
  font-size: 24px;
  font-weight: 800;
  line-height: 32px;
}

.header-actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 18px;
}

.icon-button,
.user-avatar {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 999px;
  background: transparent;
  color: #2f3a46;
}

.icon-button:hover {
  background: var(--surface-low);
  color: var(--primary);
}

.user-avatar {
  background: #d3e2ed;
  color: #56656e;
}

.suite-content {
  min-height: 0;
  flex: 1;
  overflow-y: auto;
  background: #f8f9fa;
  padding: 30px;
}

.page-stack {
  display: grid;
  gap: 30px;
  width: min(100%, 1260px);
  margin: 0 auto;
}

.search-bar {
  display: flex;
  min-height: 72px;
  align-items: center;
  gap: 18px;
  border: 1px solid var(--outline);
  border-radius: 12px;
  background: #ffffff;
  padding: 10px 12px 10px 28px;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}

.search-bar input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text);
  font-size: 20px;
}

.search-bar button,
.primary-action,
.publish-action,
.download-report,
.publish-mini,
.primary-lite {
  background: var(--primary);
  color: #ffffff;
  font-weight: 800;
}

.search-bar button {
  min-width: 100px;
  min-height: 50px;
  border: 0;
  border-radius: 10px;
  cursor: pointer;
  font-size: 20px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 30px;
}

.data-card,
.advice-card,
.hero-card,
.form-card,
.result-card,
.copy-settings-card,
.copy-preview-card,
.title-card,
.editor-card,
.publish-settings,
.account-strip,
.browser-frame {
  border: 1px solid var(--outline);
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}

.data-card {
  min-height: 232px;
  padding: 30px;
}

.data-card.tall {
  min-height: 468px;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 30px;
}

.card-title-row.with-divider {
  margin-bottom: 26px;
  border-bottom: 1px solid var(--outline);
  padding-bottom: 28px;
}

.history-inline-button {
  margin-left: auto;
  white-space: nowrap;
}

.card-title-row h2,
.advice-title h2,
.hero-card h2,
.result-card h2,
.copy-output h2,
.publish-settings h2 {
  margin: 0;
  color: #05070a;
  font-size: 22px;
  font-weight: 800;
  line-height: 28px;
}

.card-icon,
.hero-icon,
.plain-icon {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 6px;
}

.plain-icon {
  color: var(--primary);
}

.card-icon.blue,
.hero-icon {
  background: #d6e3ff;
  color: var(--primary);
}

.card-icon.red {
  background: #ffdad6;
  color: var(--error);
}

.card-icon.gray {
  background: #eef3f6;
  color: #526069;
}

.card-icon.green {
  background: #d9f1dd;
  color: var(--success);
}

.keyword-pills,
.audience-tags,
.result-tags,
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.keyword-pills span,
.audience-tags span,
.result-tags span {
  display: inline-flex;
  min-height: 38px;
  align-items: center;
  border: 1px solid var(--outline);
  border-radius: 999px;
  background: var(--surface-high);
  color: #30363d;
  font-size: 18px;
  line-height: 22px;
  padding: 7px 18px;
}

.keyword-pills span.selected,
.result-tags span {
  border-color: #a9c7ff;
  background: #d6e3ff;
  color: var(--primary-strong);
}

.hot-list,
.competitor-list {
  display: grid;
  gap: 22px;
}

.hot-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--surface-highest);
  padding-bottom: 18px;
  font-size: 18px;
}

.hot-list-item strong {
  flex: 0 0 auto;
  color: var(--primary);
  font-weight: 700;
}

.competitor-item {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 18px;
  align-items: center;
}

.competitor-badge {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 50%;
  background: var(--surface-highest);
  font-weight: 800;
}

.competitor-meta {
  display: grid;
  gap: 10px;
}

.competitor-meta div {
  display: flex;
  justify-content: space-between;
  font-size: 20px;
}

.progress-track {
  display: block;
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--surface-highest);
}

.progress-value {
  display: block;
  height: 100%;
  border-radius: inherit;
}

.bar-chart {
  display: flex;
  height: 118px;
  align-items: flex-end;
  justify-content: center;
  gap: 14px;
  margin: 10px 0 28px;
}

.bar {
  display: block;
  width: 80px;
  border-radius: 3px 3px 0 0;
}

.bar-1 {
  height: 62px;
  background: #d6e3ff;
}

.bar-2 {
  height: 102px;
  background: var(--primary);
}

.bar-3 {
  height: 82px;
  background: #a9c7ff;
}

.bar-4 {
  height: 42px;
  background: var(--surface-highest);
}

.minor-heading {
  margin: 0 0 12px;
  color: var(--text-muted);
  font-size: 16px;
}

.audience-tags {
  margin-bottom: 18px;
}

.audience-tags span {
  min-height: 30px;
  border-radius: 4px;
  font-size: 15px;
  padding: 4px 10px;
}

.persona-box {
  border-radius: 8px;
  background: var(--surface-low);
  padding: 16px;
}

.persona-box span {
  color: var(--text-muted);
  font-weight: 700;
}

.persona-box p {
  margin: 8px 0 0;
  font-size: 18px;
  line-height: 28px;
}

.advice-card {
  position: relative;
  overflow: hidden;
  border-left: 5px solid var(--success);
  padding: 36px 40px;
}

.advice-title {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 28px;
}

.advice-title svg {
  color: var(--success);
}

.advice-card ul {
  display: grid;
  gap: 16px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.advice-card li {
  display: flex;
  gap: 14px;
  font-size: 17px;
  line-height: 26px;
}

.advice-card li svg {
  width: 18px;
  height: 18px;
  margin-top: 3px;
  color: var(--primary);
}

.hero-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 22px;
  padding: 30px;
}

.hero-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
}

.hero-icon svg {
  width: 30px;
  height: 30px;
}

.hero-card p {
  margin: 6px 0 0;
  color: var(--text-muted);
}

.ghost-button {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid var(--outline);
  border-radius: 8px;
  background: #ffffff;
  color: var(--text-muted);
  font-weight: 700;
  padding: 0 18px;
}

.ghost-button:hover {
  background: var(--surface-low);
  color: var(--primary);
}

.ghost-button.compact {
  min-height: 40px;
  min-width: 88px;
}

.form-card,
.result-card {
  padding: 30px;
}

.input-field,
.select-field {
  display: grid;
  gap: 10px;
  margin-bottom: 22px;
}

.input-field span,
.select-field span,
.range-field span,
.platform-grid legend,
.radio-row legend,
.publish-platform-list legend {
  color: #111827;
  font-size: 18px;
  font-weight: 600;
}

.input-field b {
  color: var(--error);
}

.input-field input,
.input-field textarea,
.select-field select {
  width: 100%;
  border: 1px solid var(--outline);
  border-radius: 8px;
  outline: none;
  background: #ffffff;
  color: var(--text);
  font-size: 17px;
  line-height: 24px;
  transition:
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

.input-field input,
.select-field select {
  height: 48px;
  padding: 0 20px;
}

.input-field textarea {
  min-height: 120px;
  resize: vertical;
  padding: 18px 20px;
}

.input-field input:focus,
.input-field textarea:focus,
.select-field select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 88, 190, 0.12);
}

.count-field {
  position: relative;
}

.count-field em {
  position: absolute;
  right: 20px;
  bottom: 13px;
  color: var(--text-muted);
  font-style: normal;
}

.primary-action {
  display: inline-flex;
  width: 100%;
  min-height: 58px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 8px;
  font-size: 18px;
}

.primary-action:disabled {
  cursor: wait;
  opacity: 0.68;
}

.error-text {
  margin: -6px 0 16px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fef2f2;
  color: #b91c1c;
  padding: 10px 12px;
}

.success-text {
  margin: -6px 0 16px;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  background: #f0fdf4;
  color: var(--success);
  padding: 10px 12px;
}

.result-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--outline);
  padding-bottom: 10px;
}

.result-toolbar div {
  display: flex;
  gap: 12px;
}

.result-card h3 {
  margin: 24px 0 18px;
  font-size: 18px;
}

.seo-empty-state {
  display: grid;
  min-height: 220px;
  place-items: center;
  align-content: center;
  gap: 10px;
  border: 1px dashed #c8d4e8;
  border-radius: 8px;
  background: #f8fbff;
  color: var(--text-muted);
  text-align: center;
}

.seo-empty-state svg {
  width: 34px;
  height: 34px;
  color: var(--primary);
}

.seo-empty-state strong {
  color: var(--text-main);
  font-size: 18px;
}

.seo-empty-state span {
  font-size: 14px;
}

.result-tags span {
  min-height: 34px;
  font-size: 15px;
  padding: 5px 14px;
}

.suite-table {
  width: 100%;
  margin-top: 22px;
  border-collapse: collapse;
}

.suite-table th,
.suite-table td {
  border-bottom: 1px solid var(--surface-highest);
  padding: 15px 20px;
  text-align: left;
  vertical-align: top;
}

.suite-table th {
  color: #111827;
  font-weight: 800;
}

.link-action {
  background: transparent;
  color: var(--primary);
  font-weight: 700;
}

.copy-page,
.publish-page {
  display: grid;
  width: min(100%, 1260px);
  grid-template-columns: minmax(360px, 476px) minmax(0, 1fr);
  gap: 30px;
  margin: 0 auto;
}

.copy-settings-card,
.copy-preview-card {
  min-height: calc(100vh - 170px);
}

.copy-settings-card {
  display: flex;
  flex-direction: column;
  padding: 30px;
}

.range-field {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  margin-bottom: 28px;
}

.range-field input {
  grid-column: 1 / -1;
  accent-color: var(--primary);
}

.platform-grid,
.radio-row,
.publish-platform-list {
  display: grid;
  gap: 14px;
  margin: 0 0 28px;
  border: 0;
  padding: 0;
}

.platform-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.platform-grid legend,
.publish-platform-list legend,
.radio-row legend {
  grid-column: 1 / -1;
  margin-bottom: 4px;
  padding: 0;
}

.platform-grid label {
  display: flex;
  min-height: 56px;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--outline);
  border-radius: 8px;
  background: #ffffff;
  padding: 0 16px;
}

.platform-grid label.checked {
  border-color: var(--primary);
  background: #f0f6ff;
}

.platform-grid input,
.radio-row input,
.publish-platform-list input,
.agree-row input {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
}

.stick-bottom {
  margin-top: auto;
}

.copy-preview-card {
  overflow: hidden;
}

.copy-results {
  display: grid;
  gap: 30px;
  max-height: calc(100vh - 170px);
  overflow-y: auto;
  padding: 30px;
}

.copy-empty-state {
  display: grid;
  min-height: calc(100vh - 230px);
  place-items: center;
  align-content: center;
  gap: 10px;
  color: var(--text-muted);
  text-align: center;
}

.copy-empty-state svg {
  width: 34px;
  height: 34px;
  color: var(--primary);
}

.copy-empty-state strong {
  color: var(--text-main);
  font-size: 18px;
}

.copy-empty-state span {
  font-size: 14px;
}

.copy-output {
  border: 1px solid var(--outline);
  border-radius: 12px;
  padding: 30px;
}

.copy-output-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 44px;
}

.publish-mini {
  display: inline-flex;
  min-width: 100px;
  min-height: 40px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 6px;
}

.publish-mini svg {
  width: 18px;
  height: 18px;
}

.copy-output p {
  margin: 0;
  color: #111827;
  font-size: 20px;
  line-height: 34px;
  white-space: pre-wrap;
}

.publish-page {
  grid-template-columns: minmax(0, 1fr) 450px;
}

.editor-column {
  display: grid;
  gap: 20px;
}

.title-card,
.image-upload-card,
.editor-card,
.publish-settings {
  padding: 30px;
}

.tag-pill {
  display: inline-flex;
  min-height: 32px;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary-strong);
  font-weight: 700;
  padding: 4px 12px;
}

.tag-pill .tag-text {
  color: inherit;
  font-size: 15px;
  font-weight: inherit;
  line-height: 20px;
}

.tag-remove-button {
  display: inline-flex;
  width: 18px;
  height: 18px;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: transparent;
  color: inherit;
  font-size: 16px;
  font-weight: 800;
  line-height: 1;
  padding: 0;
}

.tag-remove-button:hover {
  background: rgba(0, 88, 190, 0.12);
}

.image-upload-card {
  display: grid;
  gap: 18px;
}

.publish-image-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.publish-image-head > span {
  color: #111827;
  font-size: 18px;
  font-weight: 600;
}

.publish-image-slots {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.publish-image-slot {
  display: grid;
  gap: 12px;
  min-width: 0;
  margin: 0;
}

.publish-image-preview {
  position: relative;
  display: grid;
  width: 100%;
  aspect-ratio: 16 / 9;
  place-items: center;
  overflow: hidden;
  border: 1px dashed #b8c3d6;
  border-radius: 8px;
  background: #f8fafc;
}

.publish-image-slot.status-ready .publish-image-preview {
  border-style: solid;
  border-color: var(--outline);
  background: #f1f5f9;
}

.publish-image-slot.status-failed .publish-image-preview {
  border-color: #fecaca;
  background: #fff7f7;
}

.publish-image-preview img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.publish-image-placeholder {
  display: grid;
  place-items: center;
  gap: 8px;
  color: #526070;
  padding: 18px;
}

.publish-image-placeholder svg {
  width: 30px;
  height: 30px;
  color: var(--primary);
}

.publish-image-placeholder strong {
  color: #111827;
  font-size: 16px;
}

.publish-image-skeleton {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: #e8eef7;
  animation: publish-image-pulse 1.1s ease-in-out infinite;
}

.publish-image-skeleton::before {
  position: absolute;
  inset: 0;
  content: '';
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.72), transparent);
  transform: translateX(-100%);
  animation: publish-image-shimmer 1.2s ease-in-out infinite;
}

.publish-image-skeleton span {
  position: absolute;
  left: 18px;
  right: 18px;
  height: 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.62);
}

.publish-image-skeleton span:nth-child(1) {
  top: 28%;
}

.publish-image-skeleton span:nth-child(2) {
  top: 48%;
  right: 42%;
}

.publish-image-skeleton span:nth-child(3) {
  top: 68%;
  right: 28%;
}

.publish-image-slot figcaption {
  display: grid;
  min-width: 0;
}

.generate-image-button {
  width: 100%;
  justify-content: center;
}

.publish-image-slot-error {
  margin: -2px 0 0;
  color: #b91c1c;
  font-size: 12px;
  line-height: 18px;
}

@keyframes publish-image-pulse {
  0%,
  100% {
    opacity: 0.58;
  }

  50% {
    opacity: 1;
  }
}

@keyframes publish-image-shimmer {
  100% {
    transform: translateX(100%);
  }
}

.generate-image-button:disabled,
.ghost-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.editor-card {
  display: grid;
  grid-template-rows: minmax(520px, 1fr);
  min-height: 810px;
  overflow: hidden;
  padding: 0;
}

.editor-card textarea {
  width: 100%;
  height: 100%;
  min-height: 520px;
  border: 0;
  outline: none;
  resize: none;
  color: var(--text);
  font-size: 20px;
  line-height: 32px;
  padding: 36px 30px;
}

.publish-panel {
  display: grid;
  align-content: start;
  gap: 30px;
}

.radio-row {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.radio-row label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
}

.publish-platform-list label {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  min-height: 78px;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--outline);
  border-radius: 8px;
  background: #f8fafc;
  padding: 12px 16px;
}

.publish-platform-list label.checked {
  border-color: var(--primary);
  background: #f0f6ff;
}

.publish-account-avatar {
  position: relative;
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 50%;
  color: #ffffff;
  font-size: 13px;
  font-weight: 800;
  overflow: visible;
}

.publish-account-avatar > img:not(.xhs-avatar-badge),
.publish-account-avatar .account-avatar-fallback {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  border-radius: inherit;
}

.publish-account-avatar > img:not(.xhs-avatar-badge) {
  object-fit: cover;
  background: #e5edf7;
}

.publish-account-avatar.avatar-forest .account-avatar-fallback {
  background:
    radial-gradient(circle at 35% 24%, rgba(255, 255, 255, 0.85), transparent 24%),
    linear-gradient(135deg, #263238, #5c8d6b 48%, #c7d69b);
}

.publish-account-avatar.avatar-sea .account-avatar-fallback {
  background:
    radial-gradient(circle at 35% 24%, rgba(255, 255, 255, 0.85), transparent 24%),
    linear-gradient(135deg, #1d3557, #4895ef 48%, #cfe8ff);
}

.publish-platform-list strong,
.publish-platform-list em {
  display: block;
}

.publish-platform-list em {
  margin-top: 2px;
  color: var(--success);
  font-style: normal;
  font-size: 13px;
}

.publish-platform-empty {
  margin: 0;
  border: 1px dashed var(--outline);
  border-radius: 8px;
  color: #6b7280;
  font-size: 14px;
  line-height: 22px;
  padding: 18px 16px;
}

.publish-action {
  display: flex;
  min-height: 70px;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: 10px;
  font-size: 22px;
}

.publish-action:disabled {
  cursor: wait;
  opacity: 0.68;
}

.publish-error {
  margin: 0;
}

.suite-content.page-accounts {
  overflow: hidden;
  background: #f6f8fd;
  padding: 0;
}

.accounts-page {
  display: grid;
  height: 100%;
  min-height: 0;
  grid-template-rows: auto auto minmax(0, 1fr);
  background: #f5f7fc;
}

.account-strip {
  display: flex;
  align-items: center;
  gap: 14px;
  overflow-x: auto;
  border-bottom: 1px solid #cdd3df;
  border-radius: 0;
  background: #ffffff;
  box-shadow: none;
  padding: 12px 28px;
}

.account-chip {
  position: relative;
  display: inline-grid;
  min-width: 282px;
  height: 74px;
  grid-template-columns: 46px minmax(0, 1fr);
  grid-template-rows: 26px 18px;
  align-items: center;
  column-gap: 14px;
  row-gap: 2px;
  border: 1px solid #dbe5f3;
  border-radius: 8px;
  background: #ffffff;
  color: #111827;
  cursor: pointer;
  padding: 11px 16px;
  text-align: left;
  transition:
    border-color 0.15s ease,
    background-color 0.15s ease,
    box-shadow 0.15s ease;
}

.account-chip:hover {
  border-color: #9dc0f4;
  background: #f8fbff;
}

.account-chip.active {
  border-color: #8bb8f2;
  background: #eaf3ff;
  box-shadow: inset 3px 0 0 #1d68d8, 0 1px 3px rgba(29, 104, 216, 0.12);
}

.account-avatar {
  position: relative;
  display: grid;
  grid-row: 1 / 3;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 50%;
  color: #ffffff;
  font-size: 13px;
  font-weight: 800;
  overflow: visible;
}

.account-avatar > img:not(.xhs-avatar-badge),
.account-avatar-fallback {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  border-radius: inherit;
}

.account-avatar > img:not(.xhs-avatar-badge) {
  object-fit: cover;
  background: #e5edf7;
}

.account-avatar-fallback {
  background:
    radial-gradient(circle at 35% 25%, rgba(255, 255, 255, 0.9), transparent 24%),
    linear-gradient(135deg, #234f7e, #9fc5e8 48%, #f7d48f);
}

.account-avatar.avatar-forest .account-avatar-fallback {
  background:
    radial-gradient(circle at 35% 24%, rgba(255, 255, 255, 0.85), transparent 24%),
    linear-gradient(135deg, #263238, #5c8d6b 48%, #c7d69b);
}

.account-avatar.avatar-sea .account-avatar-fallback {
  background:
    radial-gradient(circle at 35% 24%, rgba(255, 255, 255, 0.85), transparent 24%),
    linear-gradient(135deg, #1d3557, #4895ef 48%, #cfe8ff);
}

.account-avatar .xhs-avatar-badge,
.publish-account-avatar .xhs-avatar-badge {
  position: absolute;
  right: -5px;
  bottom: -4px;
  z-index: 1;
  display: block;
  width: 24px;
  height: 24px;
  border: 2px solid #ffffff;
  border-radius: 50%;
  background: #ff2442;
  box-shadow: 0 1px 3px rgba(17, 24, 39, 0.18);
  object-fit: cover;
}

.account-chip strong {
  align-self: end;
  min-width: 0;
  overflow: hidden;
  color: #111827;
  font-size: 17px;
  font-weight: 700;
  line-height: 22px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-chip em {
  color: #64748b;
  font-style: normal;
  font-weight: 500;
}

.account-chip small {
  align-self: start;
  min-width: 0;
  overflow: hidden;
  color: #64748b;
  font-size: 13px;
  line-height: 16px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  background: #f6f8fd;
  padding: 24px 28px;
}

.account-actions button {
  display: inline-flex;
  flex: 0 0 auto;
  min-height: 38px;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid #c5ccd8;
  border-radius: 6px;
  background: #ffffff;
  color: #1f2937;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
  padding: 0 14px;
  white-space: nowrap;
}

.account-actions button svg {
  width: 16px;
  height: 16px;
}

.account-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.account-actions .primary-lite {
  border-color: #1d68d8;
  background: #1d68d8;
  color: #ffffff;
}

.account-actions .danger-lite {
  border-color: #e2a3a3;
  background: #fff5f5;
  color: #b42318;
}

.login-browser-frame {
  display: grid;
  min-height: 0;
  height: 100%;
  grid-template-rows: 30px 34px minmax(0, 1fr);
  overflow: hidden;
  background: #ffffff;
}

.login-window-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #eef1f6;
  background: #ffffff;
  color: #4b5563;
  font-size: 12px;
  font-weight: 700;
  padding: 0 10px;
}

.login-window-title button {
  border: 0;
  background: transparent;
  color: #8b95a3;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.browser-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  border-top: 1px solid #edf0f5;
  border-bottom: 1px solid #edf0f5;
  background: #ffffff;
  padding: 0 12px;
}

.browser-toolbar button {
  display: grid;
  width: 18px;
  height: 18px;
  place-items: center;
  border: 0;
  background: transparent;
  color: #9aa2ad;
  cursor: pointer;
  padding: 0;
}

.browser-toolbar svg {
  width: 14px;
  height: 14px;
}

.browser-toolbar span {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  border-radius: 16px;
  background: #f2f3f5;
  color: #9aa2ad;
  font-size: 12px;
  line-height: 22px;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 12px;
}

.browser-toolbar em,
.browser-toolbar small {
  max-width: 180px;
  overflow: hidden;
  color: #7d8794;
  font-size: 11px;
  font-style: normal;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.browser-toolbar small {
  color: #111827;
}

.xiaohongshu-webview-wrap {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.xiaohongshu-webview {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 0;
  background: #ffffff;
}

.xiaohongshu-webview-empty {
  display: grid;
  flex: 1;
  min-height: 360px;
  place-items: center;
  color: #6b7280;
  font-size: 14px;
}

.suite-footer {
  display: flex;
  min-height: 56px;
  flex: 0 0 56px;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--outline);
  background: #ffffff;
  padding: 0 30px;
}

.footer-history {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  color: #30363d;
  font-size: 16px;
  font-weight: 700;
}

.download-report {
  display: inline-flex;
  min-height: 40px;
  align-items: center;
  gap: 10px;
  border-radius: 8px;
  padding: 0 18px;
}

.drawer-scrim {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(15, 23, 42, 0.48);
}

.history-drawer {
  position: absolute;
  inset: 0 0 0 auto;
  width: min(480px, 100vw);
  background: #ffffff;
  box-shadow: -20px 0 40px rgba(15, 23, 42, 0.16);
  padding: 26px 20px;
}

.history-drawer header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 36px;
}

.history-drawer h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 900;
}

.history-drawer header button {
  border: 0;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font-size: 32px;
}

.history-record {
  display: flex;
  width: 100%;
  min-height: 68px;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 16px;
  border: 1px solid var(--outline);
  border-radius: 8px;
  background: #ffffff;
  color: var(--text);
  padding: 0 20px;
  text-align: left;
  transition:
    border-color 0.15s ease,
    background-color 0.15s ease,
    box-shadow 0.15s ease;
}

.history-record:hover,
.history-record.active {
  border-color: #8bb8f2;
  background: #f0f6ff;
  box-shadow: 0 1px 4px rgba(0, 88, 190, 0.12);
}

.history-record strong {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-record span {
  color: #64748b;
  font-family: Consolas, 'JetBrains Mono', monospace;
  white-space: nowrap;
}

.history-empty-state {
  display: grid;
  min-height: 180px;
  place-items: center;
  align-content: center;
  gap: 10px;
  border: 1px dashed #c8d4e8;
  border-radius: 8px;
  background: #f8fbff;
  color: var(--text-muted);
  text-align: center;
}

.history-empty-state svg {
  width: 32px;
  height: 32px;
  color: var(--primary);
}

.history-empty-state strong {
  color: var(--text);
  font-size: 18px;
}

.history-empty-state span {
  font-size: 14px;
}

/* Reference UI polish translated from stitch_raw_canvas_importer/pages.html */
.suite-shell {
  --primary: #6b58ff;
  --primary-strong: #5140d8;
  --primary-hover: #5a47e6;
  --primary-soft: #f0eeff;
  --surface-low: #f8f9fc;
  --surface-high: #f4f6fb;
  --surface-highest: #edf0f6;
  --text: #1f2937;
  --text-muted: #6b7280;
  --outline: #e5e7eb;
  --outline-dark: #d1d5db;
  --success: #16a34a;
  background: #f8f9fc;
  color: var(--text);
  font-size: 15px;
  font-family:
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    'Microsoft YaHei',
    'PingFang SC',
    sans-serif;
}

.suite-sidebar {
  width: 116px;
  flex-basis: 116px;
  align-items: center;
  border-right: 1px solid #e5eaf2;
  border-bottom-left-radius: 18px;
  background: #ffffff;
  padding: 16px 0 18px;
}

.suite-brand {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 36px;
  padding-left: 10px;
}

.suite-brand img {
  display: block;
  width: 84px;
  height: auto;
  max-height: 38px;
  object-fit: contain;
  object-position: left center;
}

.suite-nav {
  width: 100%;
  justify-items: center;
  gap: 12px;
}

.nav-secondary {
  margin-top: 12px;
  border-top: 0;
  gap: 12px;
  padding-top: 0;
}

.nav-item,
.help-center {
  width: 88px;
  height: 96px;
  min-height: 96px;
  flex-direction: column;
  justify-content: center;
  gap: 7px;
  border-radius: 0;
  color: #657590;
  padding: 0;
  text-align: center;
  transition: none;
}

.nav-item > span:not(.nav-icon),
.help-center > span:not(.nav-icon) {
  color: #657590;
  font-size: 14.5px;
  font-weight: 500;
  line-height: 21px;
  white-space: nowrap;
}

.nav-icon {
  display: grid;
  width: 68px;
  height: 68px;
  place-items: center;
  border-radius: 20px;
  background: transparent;
  color: #8a93a2;
  transition: none;
}

.nav-icon svg {
  width: 28px;
  height: 28px;
  stroke-width: 2.35;
}

.help-center .nav-icon {
  width: 36px;
  height: 36px;
  color: #8a93a2;
}

.help-center .nav-icon svg {
  width: 30px;
  height: 30px;
}

.nav-item:hover,
.help-center:hover {
  background: transparent;
  color: #657590;
}

.nav-item.active {
  height: 96px;
  min-height: 96px;
  border-radius: 0;
  background: transparent;
  color: #657590;
  box-shadow: none;
  font-weight: 500;
}

.nav-item.active > span:not(.nav-icon) {
  color: #657590;
}

.nav-item.active .nav-icon {
  width: 68px;
  height: 68px;
  border-radius: 20px;
  background: #6b58ff;
  color: #ffffff;
  box-shadow: 0 9px 18px rgba(107, 88, 255, 0.24);
}

.nav-item.active .nav-icon svg {
  width: 32px;
  height: 32px;
  stroke-width: 2.15;
}

.help-center {
  margin-top: auto;
  background: transparent;
  color: #657590;
  font-weight: 500;
}

.suite-main {
  background: #f8f9fc;
}

.suite-header {
  height: 74px;
  flex-basis: 74px;
  border-bottom-color: #e5e7eb;
  padding: 0 30px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}

.suite-header h1,
.workspace-header h2 {
  color: #1f2937;
  font-size: 21px;
  font-weight: 800;
  line-height: 28px;
}

.suite-header p,
.workspace-header p {
  margin: 3px 0 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 20px;
}

.workspace-header strong {
  color: var(--primary);
  font-weight: 700;
}

.history-top-button {
  display: inline-flex;
  min-width: max-content;
  min-height: 28px;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #81799f;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  line-height: 20px;
  padding: 0 2px;
  white-space: nowrap;
}

.history-top-button:hover {
  background: transparent;
  color: var(--primary);
}

.history-top-button span {
  display: inline-block;
  white-space: nowrap;
}

.history-top-button svg {
  width: 15px;
  height: 15px;
  flex: 0 0 15px;
  stroke-width: 2.5;
}

.icon-button,
.user-avatar {
  width: 34px;
  height: 34px;
}

.suite-content {
  background: #f8f9fc;
  padding: 24px;
}

.suite-content.page-seo {
  overflow: hidden;
  padding: 0;
}

.reference-split-page {
  display: grid;
  height: 100%;
  min-height: 0;
  grid-template-columns: 350px minmax(0, 1fr);
}

.reference-config-panel {
  display: flex;
  min-height: 0;
  flex-direction: column;
  border-right: 1px solid #e5e7eb;
  background: #ffffff;
}

.panel-title {
  display: flex;
  min-height: 96px;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #eef0f4;
  padding: 0 24px;
}

.panel-title-icon {
  display: grid;
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  place-items: center;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary);
}

.panel-title h1 {
  margin: 0;
  color: #111827;
  font-size: 21px;
  font-weight: 800;
}

.panel-title p {
  margin: 4px 0 0;
  color: #8a90a1;
  font-size: 14px;
}

.reference-form {
  display: flex;
  min-height: 0;
  flex: 1;
  flex-direction: column;
}

.reference-fields {
  min-height: 0;
  flex: 1;
  overflow-y: auto;
  padding: 26px 24px;
}

.panel-action-bar {
  border-top: 1px solid #eef0f4;
  background: #ffffff;
  padding: 16px 24px 22px;
}

.reference-workspace {
  display: flex;
  min-width: 0;
  min-height: 0;
  flex-direction: column;
}

.workspace-header {
  display: flex;
  min-height: 96px;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 0 32px;
}

.workspace-scroll {
  min-height: 0;
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
}

.result-card,
.form-card,
.copy-settings-card,
.copy-preview-card,
.title-card,
.image-upload-card,
.editor-card,
.publish-settings {
  border-color: #edf0f5;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.seo-result-card {
  width: min(100%, 990px);
  min-height: calc(100vh - 148px);
  margin: 0 auto;
  padding: 32px 40px;
}

.result-toolbar {
  border-bottom: 0;
  padding-bottom: 18px;
}

.result-toolbar .ghost-button {
  background: #f3f4f6;
  border-color: transparent;
  color: #4b5563;
}

.seo-result-card h3 {
  margin: 24px 0 20px 38px;
  color: #111827;
  font-size: 17px;
  font-weight: 800;
}

.result-tags {
  margin: 0 38px 28px;
}

.result-tags span {
  min-height: 34px;
  border-color: #93b7ea;
  background: #eff6ff;
  color: #374151;
  font-size: 15px;
  font-weight: 600;
  padding: 5px 16px;
}

.suite-table {
  width: calc(100% - 76px);
  margin: 24px 38px 0;
}

.suite-table th,
.suite-table td {
  border-bottom-color: #edf0f5;
  padding: 13px 0;
  font-size: 15px;
}

.suite-table th {
  color: #111827;
  font-size: 15px;
}

.link-action {
  color: #2079c1;
  font-weight: 700;
}

.input-field,
.select-field {
  gap: 8px;
  margin-bottom: 20px;
}

.input-field span,
.select-field span,
.range-field span,
.platform-grid legend,
.radio-row legend,
.publish-platform-list legend,
.publish-field-block > label,
.publish-field-block > span {
  color: #374151;
  font-size: 15px;
  font-weight: 700;
}

.input-field input,
.input-field textarea,
.select-field select {
  border-color: #e5e7eb;
  border-radius: 8px;
  color: #1f2937;
  font-size: 15px;
}

.input-field input,
.select-field select {
  height: 44px;
  padding: 0 14px;
}

.input-field textarea {
  min-height: 132px;
  padding: 12px 14px;
}

.input-field input:focus,
.input-field textarea:focus,
.select-field select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(107, 88, 255, 0.13);
}

.count-field em {
  right: 14px;
  bottom: 13px;
  color: #9ca3af;
  font-size: 13px;
  font-weight: 700;
}

.primary-action,
.publish-action {
  background: var(--primary);
  color: #ffffff;
  box-shadow: 0 8px 18px rgba(107, 88, 255, 0.18);
}

.primary-action:hover,
.publish-action:hover {
  background: var(--primary-hover);
}

.primary-action {
  min-height: 52px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 800;
}

.ghost-button {
  border-color: #e5e7eb;
  border-radius: 8px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 700;
}

.suite-content.page-copywriting {
  overflow: hidden;
  padding: 0;
}

.reference-copy-page {
  width: 100%;
  height: 100%;
  min-height: 0;
  grid-template-columns: 350px minmax(0, 1fr);
  gap: 0;
  margin: 0;
}

.reference-copy-page .copy-settings-card,
.reference-copy-page .copy-preview-card {
  min-height: 0;
  border: 0;
  border-radius: 0;
  box-shadow: none;
}

.reference-copy-page .copy-settings-card {
  padding: 0;
}

.copy-reference-fields {
  padding: 26px 24px;
}

.copy-range-field {
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 10px 8px;
}

.copy-range-field em {
  color: #9ca3af;
  font-size: 14px;
  font-style: normal;
  font-weight: 700;
}

.copy-range-field strong {
  color: var(--primary);
  font-size: 17px;
  font-weight: 800;
}

.copy-range-field input {
  height: 4px;
  accent-color: var(--primary);
}

.copy-platform-field {
  display: grid;
  gap: 10px;
  margin: 0 0 20px;
  border: 0;
  padding: 0;
}

.copy-platform-field legend {
  color: #374151;
  font-size: 15px;
  font-weight: 700;
  padding: 0;
}

.copy-platform-options {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  border: 1px solid #edf0f6;
  border-radius: 12px;
  background: #f7f8fb;
  padding: 4px;
}

.copy-platform-options label {
  position: relative;
  display: flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: #374151;
  font-weight: 700;
  padding: 0 12px;
}

.copy-platform-options label.checked {
  background: var(--primary);
  color: #ffffff;
  box-shadow: 0 7px 14px rgba(107, 88, 255, 0.22);
}

.copy-platform-options input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.copy-workspace-header {
  min-height: 96px;
}

.copy-results-scroll {
  padding: 28px 32px;
}

.reference-copy-page .copy-results {
  display: grid;
  gap: 26px;
  max-height: none;
  overflow: visible;
  padding: 0;
}

.reference-copy-page .copy-empty-state {
  min-height: calc(100vh - 196px);
  border: 1px dashed #dfe4ee;
  border-radius: 16px;
  background: #ffffff;
}

.reference-copy-page .copy-output {
  border: 1px solid #edf0f5;
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
  padding: 40px 44px;
}

.reference-copy-page .copy-output-head {
  align-items: flex-start;
  margin-bottom: 30px;
}

.copy-output-title-group {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.copy-output-index {
  display: grid;
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  place-items: center;
  border-radius: 999px;
  background: var(--primary);
  color: #ffffff;
  font-size: 17px;
  font-weight: 900;
  box-shadow: 0 9px 18px rgba(107, 88, 255, 0.25);
}

.copy-output-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 10px;
  padding-top: 2px;
}

.copy-output-meta h2 {
  width: 100%;
  margin: 0;
  color: #111827;
  font-size: 21px;
  font-weight: 900;
  line-height: 26px;
}

.copy-platform-badge {
  display: inline-flex;
  min-height: 24px;
  align-items: center;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
  line-height: 18px;
  padding: 2px 10px;
}

.copy-platform-badge.platform-xhs {
  background: #fff1f2;
  color: #ff2442;
}

.copy-platform-badge.platform-wechat {
  background: #ecfdf5;
  color: #059669;
}

.reference-copy-page .publish-mini {
  min-width: 86px;
  min-height: 42px;
  border-radius: 999px;
  background: var(--primary);
  color: #ffffff;
  font-size: 15px;
  font-weight: 800;
  box-shadow: 0 8px 16px rgba(107, 88, 255, 0.22);
}

.reference-copy-page .publish-mini svg {
  width: 17px;
  height: 17px;
}

.copy-section {
  margin-top: 28px;
}

.copy-section-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 14px;
  color: #111827;
  font-size: 17px;
  font-weight: 900;
  line-height: 24px;
}

.copy-section-heading::before {
  display: block;
  width: 5px;
  height: 22px;
  border-radius: 999px;
  background: var(--primary);
  box-shadow: 0 0 0 3px rgba(107, 88, 255, 0.12);
  content: '';
}

.copy-title-text,
.copy-body-content {
  margin: 0;
  color: #172033;
  font-size: 16px;
  line-height: 30px;
}

.copy-title-text {
  font-weight: 600;
}

.copy-body-content {
  white-space: pre-wrap;
}

.copy-accent-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 26px;
}

.copy-accent-tags span {
  display: inline-flex;
  min-height: 28px;
  align-items: center;
  border: 1px solid #bfead8;
  border-radius: 999px;
  background: #ecfdf5;
  color: #059669;
  font-size: 14px;
  font-weight: 800;
  line-height: 20px;
  padding: 3px 11px;
}

.suite-content.page-publish {
  overflow: hidden;
  padding: 0;
}

.reference-publish-page {
  display: grid;
  width: 100%;
  height: 100%;
  min-height: 0;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 0;
  margin: 0;
}

.publish-subnav {
  display: flex;
  min-height: 0;
  flex-direction: column;
  border-right: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 22px 0;
}

.publish-subnav button {
  display: flex;
  min-height: 72px;
  align-items: center;
  gap: 14px;
  border: 0;
  border-right: 3px solid transparent;
  background: transparent;
  color: #374151;
  cursor: pointer;
  font-size: 17px;
  font-weight: 700;
  padding: 0 28px;
  text-align: left;
}

.publish-subnav button.active {
  border-right-color: var(--primary);
  background: #eef2ff;
  color: var(--primary);
}

.publish-subnav svg {
  width: 21px;
  height: 21px;
}

.publish-workbench {
  display: grid;
  min-width: 0;
  min-height: 0;
  height: 100%;
  align-items: stretch;
  gap: 32px;
  overflow: hidden;
  padding: 34px 34px;
}

.publish-article-workbench {
  grid-template-columns: minmax(0, 1fr) 432px;
}

.publish-image-workbench {
  grid-template-columns: minmax(0, 1fr) 510px;
}

.publish-editor-column {
  display: grid;
  min-width: 0;
  min-height: 0;
  grid-template-rows: minmax(0, 1fr) auto;
  gap: 16px;
}

.article-publish-column {
  grid-template-rows: minmax(0, 1fr);
}

.article-editor-card {
  display: flex;
  min-height: 0;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.article-publish-editor,
.image-edit-card,
.image-caption-card,
.article-side-settings,
.image-side-settings {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
}

.article-editor-head {
  display: flex;
  min-height: 58px;
  align-items: center;
  justify-content: flex-end;
  border-bottom: 1px solid #f0f2f6;
  padding: 0 18px;
}

.article-publish-editor .article-editor-head {
  min-height: 64px;
  padding: 0 26px;
}

.ai-cover-button {
  min-height: 32px;
  border: 0;
  border-radius: 999px;
  background: #eef2ff;
  color: var(--primary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 800;
  padding: 0 14px;
}

.editor-toolbar {
  display: flex;
  min-height: 52px;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
  color: #5d6472;
  padding: 6px 26px;
}

.editor-toolbar button {
  display: inline-grid;
  min-width: 28px;
  min-height: 28px;
  place-items: center;
  border: 0;
  border-radius: 5px;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 14px;
  padding: 0 7px;
  white-space: nowrap;
}

.editor-toolbar button:hover {
  background: #e5e7eb;
  color: #111827;
}

.editor-toolbar span {
  display: block;
  width: 1px;
  height: 16px;
  flex: 0 0 1px;
  background: #d1d5db;
  margin: 0 5px;
}

.tool-strong {
  font-weight: 900;
}

.tool-italic {
  font-style: italic;
}

.tool-underline {
  text-decoration: underline;
}

.tool-strike {
  text-decoration: line-through;
}

.article-editor-card textarea {
  width: 100%;
  min-height: 0;
  flex: 1;
  border: 0;
  outline: none;
  resize: none;
  color: #1f2937;
  font-size: 16px;
  line-height: 31px;
  padding: 24px 28px;
}

.article-publish-editor textarea {
  min-height: 0;
  flex: 1;
  color: #172033;
  font-size: 18px;
  line-height: 34px;
  padding: 32px 34px;
}

.article-inline-image {
  width: calc(100% - 68px);
  margin: 0 34px 34px;
  overflow: hidden;
  border-radius: 6px;
  background: #f3f4f6;
}

.article-inline-image img {
  display: block;
  width: 100%;
  max-height: 360px;
  object-fit: cover;
}

.publish-image-main {
  display: grid;
  min-width: 0;
  min-height: 0;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 34px;
}

.image-edit-card {
  padding: 36px 36px 42px;
}

.image-edit-card header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 34px;
}

.image-edit-card h2,
.image-caption-card h2 {
  margin: 0;
  color: #111827;
  font-size: 24px;
  font-weight: 900;
  line-height: 32px;
}

.image-edit-strip {
  display: flex;
  align-items: center;
  gap: 24px;
  overflow-x: auto;
  padding: 2px 2px 6px;
}

.image-add-tile,
.image-edit-thumb button {
  display: grid;
  width: 140px;
  height: 140px;
  flex: 0 0 140px;
  place-items: center;
  overflow: hidden;
  border-radius: 8px;
  background: #ffffff;
  cursor: pointer;
}

.image-add-tile {
  border: 2px dashed #d9dee8;
  color: #9ca3af;
  font-size: 52px;
  font-weight: 300;
}

.image-edit-thumb {
  display: grid;
  gap: 8px;
  margin: 0;
}

.image-edit-thumb button {
  border: 1px solid #e5e7eb;
  padding: 0;
}

.image-edit-thumb img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-thumb-placeholder,
.image-thumb-skeleton {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  background: #f8fafc;
  color: #8a93a2;
}

.image-thumb-placeholder {
  gap: 8px;
}

.image-thumb-placeholder svg {
  width: 26px;
  height: 26px;
}

.image-thumb-placeholder small {
  font-size: 13px;
  font-weight: 700;
}

.image-thumb-skeleton {
  position: relative;
  overflow: hidden;
  background: #edf0f6;
}

.image-thumb-skeleton::after {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.7), transparent);
  content: '';
  transform: translateX(-100%);
  animation: publish-image-shimmer 1.2s ease-in-out infinite;
}

.image-edit-thumb figcaption {
  max-width: 140px;
  color: #b91c1c;
  font-size: 12px;
  line-height: 17px;
}

.image-caption-card {
  display: flex;
  min-height: 0;
  flex-direction: column;
  padding: 36px;
}

.image-caption-card textarea {
  flex: 1;
  width: 100%;
  min-height: 440px;
  margin-top: 24px;
  border: 0;
  outline: none;
  resize: none;
  color: #1f2937;
  font-size: 20px;
  line-height: 34px;
}

.image-caption-card textarea::placeholder {
  color: #a3acbc;
  font-weight: 700;
}

.publish-images-compact {
  gap: 12px;
  padding: 18px;
}

.publish-images-compact .publish-image-head {
  margin: 0;
}

.publish-images-compact .publish-image-head > span {
  font-size: 16px;
  font-weight: 800;
}

.publish-images-compact .publish-image-slots {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.publish-panel {
  display: grid;
  min-width: 0;
  min-height: 0;
  height: 100%;
  grid-template-rows: minmax(0, 1fr) auto auto;
  gap: 22px;
}

.reference-publish-settings {
  min-height: 0;
  overflow-y: auto;
  padding: 30px 28px;
}

.article-side-settings,
.image-side-settings,
.publish-action-card {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
}

.image-side-settings {
  overflow: visible;
  padding: 36px;
}

.publish-action-card {
  display: grid;
  padding: 28px;
}

.publish-field-block {
  display: grid;
  gap: 12px;
  margin: 0 0 26px;
}

.cover-upload-box {
  display: grid;
  width: 100%;
  min-height: 76px;
  place-items: center;
  overflow: hidden;
  border: 1px dashed #d1d5db;
  border-radius: 8px;
  background: #ffffff;
  color: var(--primary);
  cursor: pointer;
}

.cover-upload-box:hover {
  background: #f9fafb;
  border-color: #babce3;
}

.cover-upload-box > span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  white-space: nowrap;
}

.cover-upload-box strong {
  white-space: nowrap;
}

.cover-upload-box svg {
  width: 18px;
  height: 18px;
}

.cover-upload-box img {
  display: block;
  width: 100%;
  aspect-ratio: 3.35 / 1;
  object-fit: cover;
  object-position: center;
}

.cover-reference-link {
  display: inline-flex;
  width: fit-content;
  align-items: center;
  gap: 4px;
  border: 0;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  font-size: 13px;
  padding: 0;
  white-space: nowrap;
}

.cover-reference-link:hover {
  color: var(--primary);
}

.cover-reference-link svg {
  width: 13px;
  height: 13px;
}

.reference-publish-settings .input-field textarea {
  min-height: 96px;
}

.tag-pill {
  min-height: 34px;
  background: #f3f4f6;
  color: #4b5563;
  font-size: 14px;
  padding: 5px 12px;
}

.tag-pill .tag-text {
  font-size: 14px;
  line-height: 20px;
}

.tag-remove-button {
  width: 16px;
  height: 16px;
}

.publish-platform-list {
  gap: 16px;
  margin-bottom: 0;
}

.publish-platform-list label {
  min-height: 84px;
  border-color: #e5e7eb;
  border-radius: 10px;
  background: #ffffff;
  padding: 14px 16px;
}

.publish-platform-list label.checked {
  border-color: #dedbf8;
  background: #fbfbff;
}

.publish-platform-list label.disabled {
  color: #9ca3af;
}

.publish-platform-list label.failed {
  background: #ffffff;
}

.publish-account-avatar {
  width: 36px;
  height: 36px;
}

.publish-platform-logo {
  display: grid;
  width: 50px;
  height: 50px;
  place-items: center;
  border-radius: 8px;
  color: #ffffff;
  font-weight: 900;
}

.publish-platform-logo.platform-wechat {
  background: #dcfce7;
  color: #16a34a;
}

.publish-platform-logo.platform-wechat svg {
  width: 28px;
  height: 28px;
  stroke-width: 2.4;
}

.publish-platform-logo.platform-xhs {
  background: #ff2442;
  color: #ffffff;
  font-size: 16px;
  line-height: 18px;
  text-align: center;
}

.publish-platform-logo.platform-xhs span {
  display: block;
  width: 34px;
}

.publish-platform-list strong {
  color: #1f2937;
  font-size: 17px;
  line-height: 22px;
}

.publish-platform-list em {
  position: relative;
  color: #059669;
  font-size: 12px;
  padding-left: 16px;
}

.publish-platform-list em::before {
  position: absolute;
  top: 50%;
  left: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: currentColor;
  content: '';
  transform: translateY(-50%);
}

.publish-platform-list em.failed {
  color: #ef4444;
}

.publish-platform-list input {
  width: 22px;
  height: 22px;
  accent-color: var(--primary);
}

.publish-platform-list input:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.publish-action {
  width: 100%;
  min-height: 68px;
  border-radius: 10px;
  font-size: 22px;
  font-weight: 800;
}

.visually-hidden-input {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  clip-path: inset(50%);
}

.modal-scrim {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  background: rgba(17, 24, 39, 0.48);
  backdrop-filter: blur(1px);
}

.qr-dialog,
.cover-guide-dialog {
  position: relative;
  border: 1px solid rgba(229, 231, 235, 0.9);
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.2);
}

.qr-dialog {
  width: min(654px, calc(100vw - 48px));
  min-height: 390px;
  padding: 86px 84px 70px;
}

.modal-close {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #737373;
  cursor: pointer;
  font-size: 34px;
  font-weight: 300;
  line-height: 1;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #111827;
}

.qr-dialog > .modal-close {
  position: absolute;
  top: 18px;
  right: 18px;
}

.qr-dialog-body {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 72px;
}

.qr-item {
  display: grid;
  gap: 28px;
  justify-items: center;
  margin: 0;
}

.qr-item figcaption {
  color: #202124;
  font-size: 18px;
  font-weight: 800;
}

.qr-art {
  position: relative;
  display: block;
  width: 146px;
  height: 146px;
  overflow: hidden;
  background:
    linear-gradient(#000 0 0) 10px 10px / 28px 8px no-repeat,
    linear-gradient(#000 0 0) 10px 10px / 8px 28px no-repeat,
    linear-gradient(#000 0 0) 108px 10px / 28px 8px no-repeat,
    linear-gradient(#000 0 0) 128px 10px / 8px 28px no-repeat,
    linear-gradient(#000 0 0) 10px 108px / 28px 8px no-repeat,
    linear-gradient(#000 0 0) 10px 128px / 28px 8px no-repeat,
    repeating-linear-gradient(90deg, #000 0 5px, transparent 5px 10px),
    repeating-linear-gradient(0deg, transparent 0 7px, #000 7px 10px, transparent 10px 15px),
    #ffffff;
  background-blend-mode: normal, normal, normal, normal, normal, normal, multiply, normal;
  image-rendering: pixelated;
}

.qr-art::before,
.qr-art::after {
  position: absolute;
  width: 30px;
  height: 30px;
  border: 8px solid #000;
  background: #ffffff;
  content: '';
}

.qr-art::before {
  top: 9px;
  left: 9px;
  box-shadow: 89px 0 0 -8px #fff, 89px 0 0 0 #000, 0 89px 0 -8px #fff, 0 89px 0 0 #000;
}

.qr-art::after {
  right: 18px;
  bottom: 18px;
  width: 16px;
  height: 16px;
  border-width: 5px;
}

.qr-art-two {
  background:
    linear-gradient(#000 0 0) 12px 12px / 30px 8px no-repeat,
    linear-gradient(#000 0 0) 12px 12px / 8px 30px no-repeat,
    linear-gradient(#000 0 0) 106px 12px / 28px 8px no-repeat,
    linear-gradient(#000 0 0) 126px 12px / 8px 30px no-repeat,
    linear-gradient(#000 0 0) 12px 106px / 30px 8px no-repeat,
    linear-gradient(#000 0 0) 12px 126px / 30px 8px no-repeat,
    repeating-linear-gradient(90deg, transparent 0 4px, #000 4px 9px, transparent 9px 14px),
    repeating-linear-gradient(0deg, #000 0 4px, transparent 4px 10px, #000 10px 12px, transparent 12px 17px),
    #ffffff;
}

.qr-art i {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 2;
  display: grid;
  width: 34px;
  height: 24px;
  place-items: center;
  border-radius: 3px;
  background: #ffffff;
  color: #111827;
  font-size: 8px;
  font-style: normal;
  font-weight: 900;
  transform: translate(-50%, -50%);
}

.cover-guide-dialog {
  width: min(660px, calc(100vw - 48px));
  padding: 0 56px 46px;
  text-align: center;
}

.cover-guide-dialog header {
  display: flex;
  height: 58px;
  align-items: center;
  justify-content: space-between;
  margin: 0 -34px 30px 0;
  text-align: left;
}

.cover-guide-dialog h2 {
  margin: 0;
  color: #1f2937;
  font-size: 19px;
  font-weight: 800;
}

.cover-ratio-visual {
  display: grid;
  width: min(462px, 100%);
  aspect-ratio: 3.35 / 1;
  grid-template-columns: 2.35fr 1fr;
  margin: 0 auto 18px;
}

.cover-ratio-left {
  background: #d5d5d5;
}

.cover-ratio-right {
  background: #b5b5b5;
}

.cover-guide-dialog strong {
  display: block;
  margin-bottom: 26px;
  color: #4b5563;
  font-size: 17px;
}

.cover-guide-dialog p {
  max-width: 520px;
  margin: 0 auto;
  color: #374151;
  font-size: 15px;
  font-weight: 700;
  line-height: 29px;
}

@media (max-width: 1120px) {
  .suite-sidebar {
    width: 116px;
    flex-basis: 116px;
  }

  .nav-item > span:not(.nav-icon) {
    font-size: 14.5px;
  }

  .dashboard-grid,
  .copy-page,
  .publish-page {
    grid-template-columns: 1fr;
  }

  .copy-settings-card,
  .copy-preview-card {
    min-height: auto;
  }

  .publish-page {
    width: min(100%, 900px);
  }
}

@media (max-width: 760px) {
  .suite-shell {
    display: block;
    overflow-y: auto;
  }

  .suite-sidebar {
    position: relative;
    width: 100%;
    height: auto;
    min-height: 0;
  }

  .suite-main {
    height: auto;
  }

  .suite-content {
    overflow: visible;
    padding: 20px;
  }

  .suite-header {
    position: sticky;
    top: 0;
    z-index: 10;
    height: auto;
    min-height: 68px;
  }

  .hero-card {
    grid-template-columns: 1fr;
  }

  .platform-grid,
  .radio-row {
    grid-template-columns: 1fr;
  }

  .publish-image-slots {
    grid-template-columns: 1fr;
  }

  .login-hero {
    grid-template-columns: 1fr;
  }
}
</style>
