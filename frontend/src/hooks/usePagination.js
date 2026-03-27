import { useState } from 'react'

export default function usePagination(defaultPerPage = 20) {
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(defaultPerPage)
  const [total, setTotal] = useState(0)

  const reset = () => {
    setPage(1)
    setTotal(0)
  }

  const totalPages = Math.ceil(total / perPage)

  return {
    page,
    setPage,
    perPage,
    setPerPage,
    total,
    setTotal,
    totalPages,
    reset,
  }
}
