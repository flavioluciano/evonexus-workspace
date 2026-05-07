import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../lib/api'
import Markdown from '../components/Markdown'

export default function SkillDetail() {
  const { name } = useParams()
  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (name) {
      api.getRaw(`/skills/${name}`)
        .then(setContent)
        .catch(() => setContent('# Skill not found'))
        .finally(() => setLoading(false))
    }
  }, [name])

  if (loading) {
    return (
      <div>
        <div className="skeleton h-8 w-48 mb-4 rounded" />
        <div className="skeleton h-96 rounded-xl" />
      </div>
    )
  }

  return (
    <div>
      <Link to="/skills" className="text-[#00FFA7] text-sm hover:underline mb-4 inline-block">
        &larr; Back to skills
      </Link>
      <h1 className="text-2xl font-bold text-[#F9FAFB] mb-6">{name}</h1>
      <div className="bg-[#182230] border border-[#344054] rounded-xl p-6">
        <div className="markdown-content">
          <Markdown>{content}</Markdown>
        </div>
      </div>
    </div>
  )
}
