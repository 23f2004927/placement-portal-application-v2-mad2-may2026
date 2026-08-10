<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchDrives } from '@/services/drives'
import { screenResume } from '@/services/ats'
import { useAuth } from '@/stores/auth'

/*
  One component for both roles. The drive list it offers is whatever
  GET /api/drives returns for the caller — a company sees its own postings, a
  student sees open ones — so the role scoping is inherited, not re-implemented.
*/
const auth = useAuth()

const drives = ref([])
const driveId = ref('')
const resumeText = ref('')
const result = ref(null)
const busy = ref(false)
const error = ref('')

const isCompany = computed(() => auth.role === 'company')

const driveOptions = computed(() =>
  drives.value.map((d) => ({ value: d.id, text: `${d.title} — ${d.companyName}` })),
)

onMounted(async () => {
  try {
    const data = await fetchDrives()
    drives.value = data.items
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load drives.'
  }
})

async function run() {
  error.value = ''
  result.value = null
  busy.value = true
  try {
    result.value = await screenResume(driveId.value, resumeText.value)
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not screen that resume.'
  } finally {
    busy.value = false
  }
}

function clear() {
  resumeText.value = ''
  result.value = null
  error.value = ''
}

// Bands, not a pass mark — the tool advises, it does not decide.
const tone = computed(() => {
  const score = result.value?.score
  if (score === null || score === undefined) return 'secondary'
  if (score >= 70) return 'success'
  if (score >= 40) return 'primary'
  return 'secondary'
})
</script>

<template>
  <div>
    <BAlert v-if="error" :model-value="true" variant="danger">{{ error }}</BAlert>

    <div class="ats-grid">
      <BForm class="panel" @submit.prevent="run">
        <BFormGroup label="Screen against" label-for="ats-drive" class="mb-3">
          <BFormSelect id="ats-drive" v-model="driveId" :options="driveOptions" required>
            <template #first>
              <BFormSelectOption :value="''" disabled>Choose a drive</BFormSelectOption>
            </template>
          </BFormSelect>
        </BFormGroup>

        <BFormGroup
          label="Resume text"
          label-for="ats-resume"
          :description="isCompany
            ? 'Paste the candidate\'s resume as plain text.'
            : 'Paste your resume as plain text — nothing is stored.'"
        >
          <BFormTextarea
            id="ats-resume"
            v-model="resumeText"
            rows="14"
            placeholder="Paste resume text here…"
            required
          />
        </BFormGroup>

        <div class="actions">
          <BButton variant="outline-primary" size="sm" @click="clear">Clear</BButton>
          <BButton
            type="submit"
            variant="primary"
            size="sm"
            :disabled="busy || !driveId || !resumeText.trim()"
          >
            {{ busy ? 'Screening…' : 'Screen resume' }}
          </BButton>
        </div>
      </BForm>

      <div class="panel">
        <p v-if="!result" class="hint mb-0">
          Pick a drive and paste a resume to see which of its required skills appear.
          <br /><br />
          This is a plain keyword match, not a judgement — it looks for each listed skill
          in the text and nothing more. Treat the score as a checklist, not a verdict.
        </p>

        <template v-else>
          <p class="result-drive">{{ result.driveTitle }}</p>

          <p v-if="result.score === null" class="hint">{{ result.message }}</p>

          <template v-else>
            <div class="score-row">
              <span class="score">{{ result.score }}%</span>
              <BBadge :variant="tone" class="score-tag">
                {{ result.matched.length }} of {{ result.matched.length + result.missing.length }}
                skills matched
              </BBadge>
            </div>

            <BProgress :value="result.score" :max="100" class="score-bar" :variant="tone" />

            <p class="group-label">Found in the resume</p>
            <p v-if="!result.matched.length" class="hint">None of the listed skills appeared.</p>
            <span v-for="s in result.matched" :key="s" class="chip is-hit">{{ s }}</span>

            <p class="group-label">Not found</p>
            <p v-if="!result.missing.length" class="hint">Every listed skill appeared.</p>
            <span v-for="s in result.missing" :key="s" class="chip">{{ s }}</span>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
  align-items: start;
}

.panel {
  padding: 20px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
}

.hint {
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.result-drive {
  margin: 0 0 12px;
  font-weight: 700;
}

.score-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.score {
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1;
}

.score-tag {
  padding: 4px 8px;
  font-size: 0.6875rem;
  font-weight: 700;
}

.score-bar {
  height: 6px;
  margin: 12px 0 20px;
  border-radius: 0;
}

.group-label {
  margin: 16px 0 8px;
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.chip {
  display: inline-block;
  margin: 0 4px 4px 0;
  padding: 3px 8px;
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 0.75rem;
}

.chip.is-hit {
  border-color: var(--primary);
  background: var(--primary-soft);
  color: var(--primary-hover);
  font-weight: 600;
}
</style>
