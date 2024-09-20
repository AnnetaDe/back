export function morePages(
  totalCount?: number,
  skip?: number,
  take?: number
) {
  return (skip || 0) + (take || 0) < totalCount;
}
